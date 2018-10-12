import hashlib as md5

from Crypto.Cipher import ARC4, AES
from Crypto.Hash import SHA256
from logging import getLogger

from ...utils import settings, choplist, decode_text
from ..PSStackParser import KWD
from ..PSStackParser import literal_name
from ..PSStackParser import PSEOF
from ..PDFStream import int_value, str_value, dict_value, list_value, decipher_all
from ..PDFStream import PDFObjectNotFound, PDFTypeError
from ..PDFParser import PDFStreamParser, PDFStream, PDFSyntaxError

from .exceptions import *
from .PDFSecurityHandler import PDFStandardSecurityHandler
from .PDFSecurityHandler import PDFStandardSecurityHandlerV4
from .PDFSecurityHandler import PDFStandardSecurityHandlerV5
from .PDFXRef import PDFXRefFallback, PDFXRef, PDFXRefStream

from .constants import LITERAL_CATALOG, LITERAL_OBJSTM

log = getLogger(__name__)

##  PDFDocument
##
class PDFDocument(object):

    """PDFDocument object represents a PDF document.

    Since a PDF file can be very big, normally it is not loaded at
    once. So PDF document has to cooperate with a PDF parser in order to
    dynamically import the data as processing goes.

    Typical usage:
      doc = PDFDocument(parser, password)
      obj = doc.getobj(objid)

    """

    security_handler_registry = {
        1: PDFStandardSecurityHandler,
        2: PDFStandardSecurityHandler,
    }
    if AES is not None:
        security_handler_registry[4] = PDFStandardSecurityHandlerV4
        if SHA256 is not None:
            security_handler_registry[5] = PDFStandardSecurityHandlerV5

    def __init__(self, parser, password='', caching=True, fallback=True):
        "Set the document to use a given PDFParser object."
        self.caching = caching
        self.xrefs = []
        self.info = []
        self.catalog = None
        self.encryption = None
        self.decipher = None
        self._parser = None
        self._cached_objs = {}
        self._parsed_objs = {}
        self._parser = parser
        self._parser.set_document(self)
        self.is_printable = self.is_modifiable = self.is_extractable = True
        # Retrieve the information of each header that was appended
        # (maybe multiple times) at the end of the document.
        try:
            pos = self.find_xref(parser)
            self.read_xref_from(parser, pos, self.xrefs)
        except PDFNoValidXRef:
            pass # fallback = True
        if fallback:
            parser.fallback = True
            xref = PDFXRefFallback()
            xref.load(parser)
            self.xrefs.append(xref)
        for xref in self.xrefs:
            trailer = xref.get_trailer()
            if not trailer:
                continue
            # If there's an encryption info, remember it.
            if 'Encrypt' in trailer:
                #assert not self.encryption, str(self.encryption)
                self.encryption = (list_value(trailer['ID']),
                                   dict_value(trailer['Encrypt']))
                self._initialize_password(password)
            if 'Info' in trailer:
                self.info.append(dict_value(trailer['Info']))
            if 'Root' in trailer:
                # Every PDF file must have exactly one /Root dictionary.
                self.catalog = dict_value(trailer['Root'])
                break
        else:
            raise PDFSyntaxError('No /Root object! - Is this really a PDF?')
        if self.catalog.get('Type') is not LITERAL_CATALOG:
            if settings.STRICT:
                raise PDFSyntaxError('Catalog not found!')
        return
    
    KEYWORD_OBJ = KWD(b'obj')

    # _initialize_password(password=b'')
    #   Perform the initialization with a given password.
    def _initialize_password(self, password=''):
        (docid, param) = self.encryption
        if literal_name(param.get('Filter')) != 'Standard':
            raise PDFEncryptionError('Unknown filter: param=%r' % param)
        v = int_value(param.get('V', 0))
        factory = self.security_handler_registry.get(v)
        if factory is None:
            raise PDFEncryptionError('Unknown algorithm: param=%r' % param)
        handler = factory(docid, param, password)
        self.decipher = handler.decrypt
        self.is_printable = handler.is_printable()
        self.is_modifiable = handler.is_modifiable()
        self.is_extractable = handler.is_extractable()
        self._parser.fallback = False # need to read streams with exact length
        return

    def _getobj_objstm(self, stream, index, objid):
        if stream.objid in self._parsed_objs:
            (objs, n) = self._parsed_objs[stream.objid]
        else:
            (objs, n) = self._get_objects(stream)
            if self.caching:
                self._parsed_objs[stream.objid] = (objs, n)
        i = n*2+index
        try:
            obj = objs[i]
        except IndexError:
            raise PDFSyntaxError('index too big: %r' % index)
        return obj

    def _get_objects(self, stream):
        if stream.get('Type') is not LITERAL_OBJSTM:
            if settings.STRICT:
                raise PDFSyntaxError('Not a stream object: %r' % stream)
        try:
            n = stream['N']
        except KeyError:
            if settings.STRICT:
                raise PDFSyntaxError('N is not defined: %r' % stream)
            n = 0
        parser = PDFStreamParser(stream.get_data())
        parser.set_document(self)
        objs = []
        try:
            while 1:
                (_, obj) = parser.nextobject()
                objs.append(obj)
        except PSEOF:
            pass
        return (objs, n)

    def _getobj_parse(self, pos, objid):
        self._parser.seek(pos)
        (_, objid1) = self._parser.nexttoken()  # objid
        (_, genno) = self._parser.nexttoken()  # genno
        (_, kwd) = self._parser.nexttoken()
        # #### hack around malformed pdf files
        # copied from https://github.com/jaepil/pdfminer3k/blob/master/pdfminer/pdfparser.py#L399
        #to solve https://github.com/pdfminer/pdfminer.six/issues/56
        #assert objid1 == objid, str((objid1, objid))
        if objid1 != objid:
            x = []
            while kwd is not self.KEYWORD_OBJ:
                (_,kwd) = self._parser.nexttoken()
                x.append(kwd)
            if x:
                objid1 = x[-2]
                genno = x[-1]
        # #### end hack around malformed pdf files
        if objid1 != objid:
            raise PDFSyntaxError('objid mismatch: %r=%r' % (objid1, objid))

        if kwd != KWD(b'obj'):
            raise PDFSyntaxError('Invalid object spec: offset=%r' % pos)
        (_, obj) = self._parser.nextobject()
        return obj

    # can raise PDFObjectNotFound
    def getobj(self, objid):
        assert objid != 0
        if not self.xrefs:
            raise PDFException('PDFDocument is not initialized')
        log.debug('getobj: objid=%r', objid)
        if objid in self._cached_objs:
            (obj, genno) = self._cached_objs[objid]
        else:
            for xref in self.xrefs:
                try:
                    (strmid, index, genno) = xref.get_pos(objid)
                except KeyError:
                    continue
                try:
                    if strmid is not None:
                        stream = PDFStream.validated_stream(self.getobj(strmid))
                        obj = self._getobj_objstm(stream, index, objid)
                    else:
                        obj = self._getobj_parse(index, objid)
                        if self.decipher:
                            obj = decipher_all(self.decipher, objid, genno, obj)

                    if isinstance(obj, PDFStream):
                        obj.set_objid(objid, genno)
                    break
                except (PSEOF, PDFSyntaxError):
                    continue
            else:
                raise PDFObjectNotFound(objid)
            log.debug('register: objid=%r: %r', objid, obj)
            if self.caching:
                self._cached_objs[objid] = (obj, genno)
        return obj

    def get_outlines(self):
        if 'Outlines' not in self.catalog:
            raise PDFNoOutlines

        def search(entry, level):
            entry = dict_value(entry)
            if 'Title' in entry:
                if 'A' in entry or 'Dest' in entry:
                    title = decode_text(str_value(entry['Title']))
                    dest = entry.get('Dest')
                    action = entry.get('A')
                    se = entry.get('SE')
                    yield (level, title, dest, action, se)
            if 'First' in entry and 'Last' in entry:
                for x in search(entry['First'], level+1):
                    yield x
            if 'Next' in entry:
                for x in search(entry['Next'], level):
                    yield x
            return
        return search(self.catalog['Outlines'], 0)

    def lookup_name(self, cat, key):
        try:
            names = dict_value(self.catalog['Names'])
        except (PDFTypeError, KeyError):
            raise KeyError((cat, key))
        # may raise KeyError
        d0 = dict_value(names[cat])

        def lookup(d):
            if 'Limits' in d:
                (k1, k2) = list_value(d['Limits'])
                if key < k1 or k2 < key:
                    return None
            if 'Names' in d:
                objs = list_value(d['Names'])
                names = dict(choplist(2, objs))
                return names[key]
            if 'Kids' in d:
                for c in list_value(d['Kids']):
                    v = lookup(dict_value(c))
                    if v:
                        return v
            raise KeyError((cat, key))
        return lookup(d0)

    def get_dest(self, name):
        try:
            # PDF-1.2 or later
            obj = self.lookup_name('Dests', name)
        except KeyError:
            # PDF-1.1 or prior
            if 'Dests' not in self.catalog:
                raise PDFDestinationNotFound(name)
            d0 = dict_value(self.catalog['Dests'])
            if name not in d0:
                raise PDFDestinationNotFound(name)
            obj = d0[name]
        return obj

    # find_xref
    def find_xref(self, parser):
        """Internal function used to locate the first XRef."""
        # search the last xref table by scanning the file backwards.
        prev = None
        for line in parser.revreadlines():
            line = line.strip()
            log.debug('find_xref: %r', line)
            if line == b'startxref':
                break
            if line:
                prev = line
        else:
            raise PDFNoValidXRef('Unexpected EOF')
        log.info('xref found: pos=%r', prev)
        return int(prev)

    # read xref table
    def read_xref_from(self, parser, start, xrefs):
        """Reads XRefs from the given location."""
        parser.seek(start)
        parser.reset()
        try:
            (pos, token) = parser.nexttoken()
        except PSEOF:
            raise PDFNoValidXRef('Unexpected EOF')
        log.info('read_xref_from: start=%d, token=%r', start, token)
        if isinstance(token, int):
            # XRefStream: PDF-1.5
            parser.seek(pos)
            parser.reset()
            xref = PDFXRefStream()
            xref.load(parser)
        else:
            if token is parser.KEYWORD_XREF:
                parser.nextline()
            xref = PDFXRef()
            xref.load(parser)
        xrefs.append(xref)
        trailer = xref.get_trailer()
        log.info('trailer: %r', trailer)
        if 'XRefStm' in trailer:
            pos = int_value(trailer['XRefStm'])
            self.read_xref_from(parser, pos, xrefs)
        if 'Prev' in trailer:
            # find previous xref
            pos = int_value(trailer['Prev'])
            self.read_xref_from(parser, pos, xrefs)
        return
