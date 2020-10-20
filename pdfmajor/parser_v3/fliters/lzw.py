from io import BytesIO
from typing import List, Optional
from ..exceptions import DecodeFailed

##  LZWDecoder
##
class LZWDecoder(object):
    def __init__(self, fp: BytesIO):
        self.fp = fp
        self.buff: int = 0
        self.bpos: int = 8
        self.nbits: int = 9
        self.table: Optional[List[bytes]] = None
        self.prevbuf: Optional[bytes] = None
        return

    def readbits(self, bits):
        v = 0
        while 1:
            # the number of remaining bits we can get from the current buffer.
            r = 8 - self.bpos
            if bits <= r:
                # |-----8-bits-----|
                # |-bpos-|-bits-|  |
                # |      |----r----|
                v = (v << bits) | ((self.buff >> (r - bits)) & ((1 << bits) - 1))
                self.bpos += bits
                break
            else:
                # |-----8-bits-----|
                # |-bpos-|---bits----...
                # |      |----r----|
                v = (v << r) | (self.buff & ((1 << r) - 1))
                bits -= r
                x = self.fp.read(1)
                if not x:
                    raise EOFError
                self.buff = ord(x)
                self.bpos = 0
        return v

    def feed(self, code):
        x = b""
        if code == 256:
            self.table = [bytes([c]) for c in range(256)]  # 0-255
            self.table.append(None)  # 256
            self.table.append(None)  # 257
            self.prevbuf = b""
            self.nbits = 9
        elif code == 257:
            pass
        elif not self.prevbuf:
            x = self.prevbuf = self.table[code]
        else:
            if code < len(self.table):
                x = self.table[code]
                self.table.append(self.prevbuf + x[:1])
            elif code == len(self.table):
                self.table.append(self.prevbuf + self.prevbuf[:1])
                x = self.table[code]
            else:
                raise DecodeFailed("LZW")
            l = len(self.table)
            if l == 511:
                self.nbits = 10
            elif l == 1023:
                self.nbits = 11
            elif l == 2047:
                self.nbits = 12
            self.prevbuf = x
        return x

    def run(self):
        while 1:
            try:
                code = self.readbits(self.nbits)
                x = self.feed(code)
            except EOFError:
                break
            yield x
        return


# lzwdecode
def lzwdecode(data: bytes):
    fp = BytesIO(data)
    s = LZWDecoder(fp).run()
    return b"".join(s)
