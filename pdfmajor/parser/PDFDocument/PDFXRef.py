import re
from logging import getLogger

from ...utils import settings, choplist, nunpack
from ..PSStackParser import PSEOF
from ..PSStackParser import KWD
from ..PDFParser import PDFStreamParser
from ..PDFStream import PDFStream
from ..PDFStream import dict_value

from .constants import LITERAL_OBJSTM, LITERAL_XREF
from .exceptions import PDFNoValidXRef, PDFSyntaxError


log = getLogger(__name__)

##  XRefs
##
class PDFBaseXRef(object):

    def get_trailer(self):
        raise NotImplementedError

    def get_objids(self):
        return []

    # Must return
    #     (strmid, index, genno)
    #  or (None, pos, genno)
    def get_pos(self, objid):
        raise KeyError(objid)


##  PDFXRef
##
class PDFXRef(PDFBaseXRef):

    def __init__(self):
        self.offsets = {}
        self.trailer = {}
        return

    def __repr__(self):
        return '<PDFXRef: offsets=%r>' % (self.offsets.keys())

    def load(self, parser):
        while True:
            try:
                (pos, line) = parser.nextline()
                if not line.strip():
                    continue
            except PSEOF:
                raise PDFNoValidXRef('Unexpected EOF - file corrupted?')
            if not line:
                raise PDFNoValidXRef('Premature eof: %r' % parser)
            if line.startswith(b'trailer'):
                parser.seek(pos)
                break
            f = line.strip().split(b' ')
            if len(f) != 2:
                raise PDFNoValidXRef('Trailer not found: %r: line=%r' % (parser, line))
            try:
                (start, nobjs) = map(int, f)
            except ValueError:
                raise PDFNoValidXRef('Invalid line: %r: line=%r' % (parser, line))
            for objid in range(start, start+nobjs):
                try:
                    (_, line) = parser.nextline()
                except PSEOF:
                    raise PDFNoValidXRef('Unexpected EOF - file corrupted?')
                f = line.strip().split(b' ')
                if len(f) != 3:
                    raise PDFNoValidXRef('Invalid XRef format: %r, line=%r' % (parser, line))
                (pos, genno, use) = f
                if use != b'n':
                    continue
                self.offsets[objid] = (None, int(pos), int(genno))
        log.info('xref objects: %r', self.offsets)
        self.load_trailer(parser)
        return

    def load_trailer(self, parser):
        try:
            (_, kwd) = parser.nexttoken()
            assert kwd is KWD(b'trailer'), str(kwd)
            (_, dic) = parser.nextobject()
        except PSEOF:
            x = parser.pop(1)
            if not x:
                raise PDFNoValidXRef('Unexpected EOF - file corrupted')
            (_, dic) = x[0]
        self.trailer.update(dict_value(dic))
        log.debug('trailer=%r', self.trailer)
        return

    def get_trailer(self):
        return self.trailer

    def get_objids(self):
        return iter(self.offsets.keys())

    def get_pos(self, objid):
        try:
            return self.offsets[objid]
        except KeyError:
            raise


##  PDFXRefFallback
##
class PDFXRefFallback(PDFXRef):

    def __repr__(self):
        return '<PDFXRefFallback: offsets=%r>' % (self.offsets.keys())

    PDFOBJ_CUE = re.compile(r'^(\d+)\s+(\d+)\s+obj\b')

    def load(self, parser):
        parser.seek(0)
        while 1:
            try:
                (pos, line) = parser.nextline()
            except PSEOF:
                break
            if line.startswith(b'trailer'):
                parser.seek(pos)
                self.load_trailer(parser)
                log.info('trailer: %r', self.trailer)
                break
            line=line.decode('latin-1') #default pdf encoding
            m = self.PDFOBJ_CUE.match(line)
            if not m:
                continue
            (objid, genno) = m.groups()
            objid = int(objid)
            genno = int(genno)
            self.offsets[objid] = (None, pos, genno)
            # expand ObjStm.
            parser.seek(pos)
            (_, obj) = parser.nextobject()
            if isinstance(obj, PDFStream) and obj.get('Type') is LITERAL_OBJSTM:
                stream = PDFStream.validated_stream(obj)
                try:
                    n = stream['N']
                except KeyError:
                    if settings.STRICT:
                        raise PDFSyntaxError('N is not defined: %r' % stream)
                    n = 0
                parser1 = PDFStreamParser(stream.get_data())
                objs = []
                try:
                    while 1:
                        (_, obj) = parser1.nextobject()
                        objs.append(obj)
                except PSEOF:
                    pass
                n = min(n, len(objs)//2)
                for index in range(n):
                    objid1 = objs[index*2]
                    self.offsets[objid1] = (objid, index, 0)
        return

##  PDFXRefStream
##
class PDFXRefStream(PDFBaseXRef):

    def __init__(self):
        self.data = None
        self.entlen = None
        self.fl1 = self.fl2 = self.fl3 = None
        self.ranges = []
        return

    def __repr__(self):
        return '<PDFXRefStream: ranges=%r>' % (self.ranges)

    def load(self, parser):
        (_, objid) = parser.nexttoken()  # ignored
        (_, genno) = parser.nexttoken()  # ignored
        (_, kwd) = parser.nexttoken()
        (_, stream) = parser.nextobject()
        if not isinstance(stream, PDFStream) or stream['Type'] is not LITERAL_XREF:
            raise PDFNoValidXRef('Invalid PDF stream spec.')
        size = stream['Size']
        index_array = stream.get('Index', (0, size))
        if len(index_array) % 2 != 0:
            raise PDFSyntaxError('Invalid index number')
        self.ranges.extend(choplist(2, index_array))
        (self.fl1, self.fl2, self.fl3) = stream['W']
        self.data = stream.get_data()
        self.entlen = self.fl1+self.fl2+self.fl3
        self.trailer = stream.attrs
        log.info('xref stream: objid=%s, fields=%d,%d,%d',
                 ', '.join(map(repr, self.ranges)),
                 self.fl1, self.fl2, self.fl3)
        return

    def get_trailer(self):
        return self.trailer

    def get_objids(self):
        for (start, nobjs) in self.ranges:
            for i in range(nobjs):
                offset = self.entlen * i
                ent = self.data[offset:offset+self.entlen]
                f1 = nunpack(ent[:self.fl1], 1)
                if f1 == 1 or f1 == 2:
                    yield start+i
        return

    def get_pos(self, objid):
        index = 0
        for (start, nobjs) in self.ranges:
            if start <= objid and objid < start+nobjs:
                index += objid - start
                break
            else:
                index += nobjs
        else:
            raise KeyError(objid)
        offset = self.entlen * index
        ent = self.data[offset:offset+self.entlen]
        f1 = nunpack(ent[:self.fl1], 1)
        f2 = nunpack(ent[self.fl1:self.fl1+self.fl2])
        f3 = nunpack(ent[self.fl1+self.fl2:])
        if f1 == 1:
            return (None, f2, f3)
        elif f1 == 2:
            return (f2, f3, 0)
        else:
            # this is a free object
            raise KeyError(objid)
