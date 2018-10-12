import hashlib as md5

from Crypto.Cipher import ARC4, AES
from Crypto.Hash import SHA256

from .exceptions import * # pylint: disable=W0614
from ..PDFStream import int_value, str_value, dict_value
from ..PSStackParser import literal_name
from ...utils import int2byte, struct

##  PDFSecurityHandler
##
class PDFStandardSecurityHandler(object):

    PASSWORD_PADDING = (b'(\xbfN^Nu\x8aAd\x00NV\xff\xfa\x01\x08'
                        b'..\x00\xb6\xd0h>\x80/\x0c\xa9\xfedSiz')
    supported_revisions = (2, 3)

    def __init__(self, docid, param, password=''):
        self.docid = docid
        self.param = param
        self.password = password
        self.encrypt_metadata = False
        self.init()
        return

    def init(self):
        self.init_params()
        if self.r not in self.supported_revisions:
            raise PDFEncryptionError('Unsupported revision: param=%r' % self.param)
        self.init_key()
        return

    def init_params(self):
        self.v = int_value(self.param.get('V', 0))
        self.r = int_value(self.param['R'])
        self.p = int_value(self.param['P'])
        self.o = str_value(self.param['O'])
        self.u = str_value(self.param['U'])
        self.length = int_value(self.param.get('Length', 40))
        return

    def init_key(self):
        self.key = self.authenticate(self.password)
        if self.key is None:
            raise PDFPasswordIncorrect
        return

    def is_printable(self):
        return bool(self.p & 4)

    def is_modifiable(self):
        return bool(self.p & 8)

    def is_extractable(self):
        return bool(self.p & 16)

    def compute_u(self, key):
        if self.r == 2:
            # Algorithm 3.4
            return ARC4.new(key).encrypt(self.PASSWORD_PADDING)  # 2
        else:
            # Algorithm 3.5
            hash = md5.md5(self.PASSWORD_PADDING)  # 2
            hash.update(self.docid[0])  # 3
            result = ARC4.new(key).encrypt(hash.digest())  # 4
            for i in range(1, 20):  # 5
                k = b''.join(int2byte(c ^ i) for c in iter(key))
                result = ARC4.new(k).encrypt(result)
            result += result  # 6
            return result

    def compute_encryption_key(self, password):
        # Algorithm 3.2
        password = (password + self.PASSWORD_PADDING)[:32]  # 1
        hash = md5.md5(password)  # 2
        hash.update(self.o)  # 3
        hash.update(struct.pack('<l', self.p))  # 4
        hash.update(self.docid[0])  # 5
        if self.r >= 4:
            if not self.encrypt_metadata:
                hash.update(b'\xff\xff\xff\xff')
        result = hash.digest()
        n = 5
        if self.r >= 3:
            n = self.length // 8
            for _ in range(50):
                result = md5.md5(result[:n]).digest()
        return result[:n]

    def authenticate(self, password):
        password = password.encode("latin1")
        key = self.authenticate_user_password(password)
        if key is None:
            key = self.authenticate_owner_password(password)
        return key

    def authenticate_user_password(self, password):
        key = self.compute_encryption_key(password)
        if self.verify_encryption_key(key):
            return key
        else:
            return None

    def verify_encryption_key(self, key):
        # Algorithm 3.6
        u = self.compute_u(key)
        if self.r == 2:
            return u == self.u
        return u[:16] == self.u[:16]

    def authenticate_owner_password(self, password):
        # Algorithm 3.7
        password = (password + self.PASSWORD_PADDING)[:32]
        hash = md5.md5(password)
        if self.r >= 3:
            for _ in range(50):
                hash = md5.md5(hash.digest())
        n = 5
        if self.r >= 3:
            n = self.length // 8
        key = hash.digest()[:n]
        if self.r == 2:
            user_password = ARC4.new(key).decrypt(self.o)
        else:
            user_password = self.o
            for i in range(19, -1, -1):
                k = b''.join(int2byte(c ^ i) for c in iter(key))
                user_password = ARC4.new(k).decrypt(user_password)
        return self.authenticate_user_password(user_password)

    def decrypt(self, objid, genno, data, attrs=None):
        return self.decrypt_rc4(objid, genno, data)

    def decrypt_rc4(self, objid, genno, data):
        key = self.key + struct.pack('<L', objid)[:3] + struct.pack('<L', genno)[:2]
        hash = md5.md5(key)
        key = hash.digest()[:min(len(key), 16)]
        return ARC4.new(key).decrypt(data)


class PDFStandardSecurityHandlerV4(PDFStandardSecurityHandler):

    supported_revisions = (4,)

    def init_params(self):
        super(PDFStandardSecurityHandlerV4, self).init_params()
        self.length = 128
        self.cf = dict_value(self.param.get('CF'))
        self.stmf = literal_name(self.param['StmF'])
        self.strf = literal_name(self.param['StrF'])
        self.encrypt_metadata = bool(self.param.get('EncryptMetadata', True))
        if self.stmf != self.strf:
            raise PDFEncryptionError('Unsupported crypt filter: param=%r' % self.param)
        self.cfm = {}
        for k, v in self.cf.items():
            f = self.get_cfm(literal_name(v['CFM']))
            if f is None:
                raise PDFEncryptionError('Unknown crypt filter method: param=%r' % self.param)
            self.cfm[k] = f
        self.cfm['Identity'] = self.decrypt_identity
        if self.strf not in self.cfm:
            raise PDFEncryptionError('Undefined crypt filter: param=%r' % self.param)
        return

    def get_cfm(self, name):
        if name == 'V2':
            return self.decrypt_rc4
        elif name == 'AESV2':
            return self.decrypt_aes128
        else:
            return None

    def decrypt(self, objid, genno, data, attrs=None, name=None):
        if not self.encrypt_metadata and attrs is not None:
            t = attrs.get('Type')
            if t is not None and literal_name(t) == 'Metadata':
                return data
        if name is None:
            name = self.strf
        return self.cfm[name](objid, genno, data)

    def decrypt_identity(self, objid, genno, data):
        return data

    def decrypt_aes128(self, objid, genno, data):
        key = self.key + struct.pack('<L', objid)[:3] + struct.pack('<L', genno)[:2] + b'sAlT'
        hash = md5.md5(key)
        key = hash.digest()[:min(len(key), 16)]
        return AES.new(key, mode=AES.MODE_CBC, IV=data[:16]).decrypt(data[16:])


class PDFStandardSecurityHandlerV5(PDFStandardSecurityHandlerV4):

    supported_revisions = (5,)

    def init_params(self):
        super(PDFStandardSecurityHandlerV5, self).init_params()
        self.length = 256
        self.oe = str_value(self.param['OE'])
        self.ue = str_value(self.param['UE'])
        self.o_hash = self.o[:32]
        self.o_validation_salt = self.o[32:40]
        self.o_key_salt = self.o[40:]
        self.u_hash = self.u[:32]
        self.u_validation_salt = self.u[32:40]
        self.u_key_salt = self.u[40:]
        return

    def get_cfm(self, name):
        if name == 'AESV3':
            return self.decrypt_aes256
        else:
            return None

    def authenticate(self, password):
        password = password.encode('utf-8')[:127]
        hash = SHA256.new(password)
        hash.update(self.o_validation_salt)
        hash.update(self.u)
        if hash.digest() == self.o_hash:
            hash = SHA256.new(password)
            hash.update(self.o_key_salt)
            hash.update(self.u)
            return AES.new(hash.digest(), mode=AES.MODE_CBC, IV=b'\x00' * 16).decrypt(self.oe)
        hash = SHA256.new(password)
        hash.update(self.u_validation_salt)
        if hash.digest() == self.u_hash:
            hash = SHA256.new(password)
            hash.update(self.u_key_salt)
            return AES.new(hash.digest(), mode=AES.MODE_CBC, IV=b'\x00' * 16).decrypt(self.ue)
        return None

    def decrypt_aes256(self, objid, genno, data):
        return AES.new(self.key, mode=AES.MODE_CBC, IV=data[:16]).decrypt(data[16:])
