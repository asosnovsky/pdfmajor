import zlib

from ...utils import lzwdecode
from ...utils import ascii85decode, asciihexdecode, apply_png_predictor

from .constants import * 
from .types import * 
from .exceptions import * 
from .util import *
from .ccitt import ccittfaxdecode

class PDFStream(PDFObject):

    @classmethod
    def validated_stream(cls, x):
        x = resolve1(x)
        if not isinstance(x, cls):
            if settings.STRICT:
                raise PDFTypeError('PDFStream required: %r' % x)
            return PDFStream({}, b'')
        return x

    def __init__(self, attrs, rawdata, decipher=None):
        assert isinstance(attrs, dict), str(type(attrs))
        self.attrs = attrs
        self.rawdata = rawdata
        self.decipher = decipher
        self.data = None
        self.objid = None
        self.genno = None
        return

    def set_objid(self, objid, genno):
        self.objid = objid
        self.genno = genno
        return

    def __repr__(self):
        if self.data is None:
            assert self.rawdata is not None
            return '<PDFStream(%r): raw=%d, %r>' % (self.objid, len(self.rawdata), self.attrs)
        else:
            assert self.data is not None
            return '<PDFStream(%r): len=%d, %r>' % (self.objid, len(self.data), self.attrs)

    def __contains__(self, name):
        return name in self.attrs

    def __getitem__(self, name):
        return self.attrs[name]

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def get_any(self, names, default=None):
        for name in names:
            if name in self.attrs:
                return self.attrs[name]
        return default

    def get_filters(self):
        filters = self.get_any(('F', 'Filter'))
        params = self.get_any(('DP', 'DecodeParms', 'FDecodeParms'), {})
        if not filters:
            return []
        if not isinstance(filters, list):
            filters = [filters]
        if not isinstance(params, list):
            # Make sure the parameters list is the same as filters.
            params = [params] * len(filters)
        if settings.STRICT and len(params) != len(filters):
            raise PDFException("Parameters len filter mismatch")
        # resolve filter if possible
        _filters = []
        for fltr in filters:
            if hasattr(fltr, 'resolve'):
                fltr = fltr.resolve()[0]
            _filters.append(fltr)
        return list(zip(_filters, params)) #solves https://github.com/pdfminer/pdfminer.six/issues/15

    def decode(self):
        assert self.data is None and self.rawdata is not None, str((self.data, self.rawdata))
        data = self.rawdata
        if self.decipher:
            # Handle encryption
            data = self.decipher(self.objid, self.genno, data, self.attrs)
        filters = self.get_filters()
        if not filters:
            self.data = data
            self.rawdata = None
            return
        for (f,params) in filters:
            if f in LITERALS_FLATE_DECODE:
                # will get errors if the document is encrypted.
                try:
                    data = zlib.decompress(data)
                except zlib.error as e:
                    if settings.STRICT:
                        raise PDFException('Invalid zlib bytes: %r, %r' % (e, data))
                    data = b''
            elif f in LITERALS_LZW_DECODE:
                data = lzwdecode(data)
            elif f in LITERALS_ASCII85_DECODE:
                data = ascii85decode(data)
            elif f in LITERALS_ASCIIHEX_DECODE:
                data = asciihexdecode(data)
            elif f in LITERALS_RUNLENGTH_DECODE:
                data = rldecode(data)
            elif f in LITERALS_CCITTFAX_DECODE:
                data = ccittfaxdecode(data, params)
            elif f in LITERALS_DCT_DECODE:
                # This is probably a JPG stream - it does not need to be decoded twice.
                # Just return the stream to the user.
                pass
            elif f == LITERAL_CRYPT:
                # not yet..
                raise PDFNotImplementedError('/Crypt filter is unsupported')
            else:
                raise PDFNotImplementedError('Unsupported filter: %r' % f)
            # apply predictors
            if params and 'Predictor' in params:
                pred = int_value(params['Predictor'])
                if pred == 1:
                    # no predictor
                    pass
                elif 10 <= pred:
                    # PNG predictor
                    colors = int_value(params.get('Colors', 1))
                    columns = int_value(params.get('Columns', 1))
                    bitspercomponent = int_value(params.get('BitsPerComponent', 8))
                    data = apply_png_predictor(pred, colors, columns, bitspercomponent, data)
                else:
                    raise PDFNotImplementedError('Unsupported predictor: %r' % pred)
        self.data = data
        self.rawdata = None
        return

    def get_data(self):
        if self.data is None:
            self.decode()
        return self.data

    def get_rawdata(self):
        return self.rawdata