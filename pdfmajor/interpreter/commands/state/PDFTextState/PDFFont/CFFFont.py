##  CFFFont
##  (Format specified in Adobe Technical Note: #5176
##   "The Compact Font Format Specification")
##
import struct
from io import BytesIO
from pdfmajor.utils import nunpack

NIBBLES = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'e', 'e-', None, '-')

def getdict(data):
    d = {}
    fp = BytesIO(data)
    stack = []
    while 1:
        c = fp.read(1)
        if not c:
            break
        b0 = ord(c)
        if b0 <= 21:
            d[b0] = stack
            stack = []
            continue
        if b0 == 30:
            s = ''
            loop = True
            while loop:
                b = ord(fp.read(1))
                for n in (b >> 4, b & 15):
                    if n == 15:
                        loop = False
                    else:
                        s += NIBBLES[n]
            value = float(s)
        elif 32 <= b0 and b0 <= 246:
            value = b0-139
        else:
            b1 = ord(fp.read(1))
            if 247 <= b0 and b0 <= 250:
                value = ((b0-247) << 8)+b1+108
            elif 251 <= b0 and b0 <= 254:
                value = -((b0-251) << 8)-b1-108
            else:
                b2 = ord(fp.read(1))
                if 128 <= b1:
                    b1 -= 256
                if b0 == 28:
                    value = b1 << 8 | b2
                else:
                    value = b1 << 24 | b2 << 16 | struct.unpack('>H', fp.read(2))[0]
        stack.append(value)
    return d


class CFFFont(object):

    STANDARD_STRINGS = (
      '.notdef', 'space', 'exclam', 'quotedbl', 'numbersign',
      'dollar', 'percent', 'ampersand', 'quoteright', 'parenleft',
      'parenright', 'asterisk', 'plus', 'comma', 'hyphen', 'period',
      'slash', 'zero', 'one', 'two', 'three', 'four', 'five', 'six',
      'seven', 'eight', 'nine', 'colon', 'semicolon', 'less', 'equal',
      'greater', 'question', 'at', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
      'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
      'U', 'V', 'W', 'X', 'Y', 'Z', 'bracketleft', 'backslash',
      'bracketright', 'asciicircum', 'underscore', 'quoteleft', 'a',
      'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
      'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
      'braceleft', 'bar', 'braceright', 'asciitilde', 'exclamdown',
      'cent', 'sterling', 'fraction', 'yen', 'florin', 'section',
      'currency', 'quotesingle', 'quotedblleft', 'guillemotleft',
      'guilsinglleft', 'guilsinglright', 'fi', 'fl', 'endash',
      'dagger', 'daggerdbl', 'periodcentered', 'paragraph', 'bullet',
      'quotesinglbase', 'quotedblbase', 'quotedblright',
      'guillemotright', 'ellipsis', 'perthousand', 'questiondown',
      'grave', 'acute', 'circumflex', 'tilde', 'macron', 'breve',
      'dotaccent', 'dieresis', 'ring', 'cedilla', 'hungarumlaut',
      'ogonek', 'caron', 'emdash', 'AE', 'ordfeminine', 'Lslash',
      'Oslash', 'OE', 'ordmasculine', 'ae', 'dotlessi', 'lslash',
      'oslash', 'oe', 'germandbls', 'onesuperior', 'logicalnot', 'mu',
      'trademark', 'Eth', 'onehalf', 'plusminus', 'Thorn',
      'onequarter', 'divide', 'brokenbar', 'degree', 'thorn',
      'threequarters', 'twosuperior', 'registered', 'minus', 'eth',
      'multiply', 'threesuperior', 'copyright', 'Aacute',
      'Acircumflex', 'Adieresis', 'Agrave', 'Aring', 'Atilde',
      'Ccedilla', 'Eacute', 'Ecircumflex', 'Edieresis', 'Egrave',
      'Iacute', 'Icircumflex', 'Idieresis', 'Igrave', 'Ntilde',
      'Oacute', 'Ocircumflex', 'Odieresis', 'Ograve', 'Otilde',
      'Scaron', 'Uacute', 'Ucircumflex', 'Udieresis', 'Ugrave',
      'Yacute', 'Ydieresis', 'Zcaron', 'aacute', 'acircumflex',
      'adieresis', 'agrave', 'aring', 'atilde', 'ccedilla', 'eacute',
      'ecircumflex', 'edieresis', 'egrave', 'iacute', 'icircumflex',
      'idieresis', 'igrave', 'ntilde', 'oacute', 'ocircumflex',
      'odieresis', 'ograve', 'otilde', 'scaron', 'uacute',
      'ucircumflex', 'udieresis', 'ugrave', 'yacute', 'ydieresis',
      'zcaron', 'exclamsmall', 'Hungarumlautsmall', 'dollaroldstyle',
      'dollarsuperior', 'ampersandsmall', 'Acutesmall',
      'parenleftsuperior', 'parenrightsuperior', 'twodotenleader',
      'onedotenleader', 'zerooldstyle', 'oneoldstyle', 'twooldstyle',
      'threeoldstyle', 'fouroldstyle', 'fiveoldstyle', 'sixoldstyle',
      'sevenoldstyle', 'eightoldstyle', 'nineoldstyle',
      'commasuperior', 'threequartersemdash', 'periodsuperior',
      'questionsmall', 'asuperior', 'bsuperior', 'centsuperior',
      'dsuperior', 'esuperior', 'isuperior', 'lsuperior', 'msuperior',
      'nsuperior', 'osuperior', 'rsuperior', 'ssuperior', 'tsuperior',
      'ff', 'ffi', 'ffl', 'parenleftinferior', 'parenrightinferior',
      'Circumflexsmall', 'hyphensuperior', 'Gravesmall', 'Asmall',
      'Bsmall', 'Csmall', 'Dsmall', 'Esmall', 'Fsmall', 'Gsmall',
      'Hsmall', 'Ismall', 'Jsmall', 'Ksmall', 'Lsmall', 'Msmall',
      'Nsmall', 'Osmall', 'Psmall', 'Qsmall', 'Rsmall', 'Ssmall',
      'Tsmall', 'Usmall', 'Vsmall', 'Wsmall', 'Xsmall', 'Ysmall',
      'Zsmall', 'colonmonetary', 'onefitted', 'rupiah', 'Tildesmall',
      'exclamdownsmall', 'centoldstyle', 'Lslashsmall', 'Scaronsmall',
      'Zcaronsmall', 'Dieresissmall', 'Brevesmall', 'Caronsmall',
      'Dotaccentsmall', 'Macronsmall', 'figuredash', 'hypheninferior',
      'Ogoneksmall', 'Ringsmall', 'Cedillasmall', 'questiondownsmall',
      'oneeighth', 'threeeighths', 'fiveeighths', 'seveneighths',
      'onethird', 'twothirds', 'zerosuperior', 'foursuperior',
      'fivesuperior', 'sixsuperior', 'sevensuperior', 'eightsuperior',
      'ninesuperior', 'zeroinferior', 'oneinferior', 'twoinferior',
      'threeinferior', 'fourinferior', 'fiveinferior', 'sixinferior',
      'seveninferior', 'eightinferior', 'nineinferior',
      'centinferior', 'dollarinferior', 'periodinferior',
      'commainferior', 'Agravesmall', 'Aacutesmall',
      'Acircumflexsmall', 'Atildesmall', 'Adieresissmall',
      'Aringsmall', 'AEsmall', 'Ccedillasmall', 'Egravesmall',
      'Eacutesmall', 'Ecircumflexsmall', 'Edieresissmall',
      'Igravesmall', 'Iacutesmall', 'Icircumflexsmall',
      'Idieresissmall', 'Ethsmall', 'Ntildesmall', 'Ogravesmall',
      'Oacutesmall', 'Ocircumflexsmall', 'Otildesmall',
      'Odieresissmall', 'OEsmall', 'Oslashsmall', 'Ugravesmall',
      'Uacutesmall', 'Ucircumflexsmall', 'Udieresissmall',
      'Yacutesmall', 'Thornsmall', 'Ydieresissmall', '001.000',
      '001.001', '001.002', '001.003', 'Black', 'Bold', 'Book',
      'Light', 'Medium', 'Regular', 'Roman', 'Semibold',
    )

    class INDEX(object):

        def __init__(self, fp):
            self.fp = fp
            self.offsets = []
            (count, offsize) = struct.unpack('>HB', self.fp.read(3))
            for _ in range(count+1):
                self.offsets.append(nunpack(self.fp.read(offsize)))
            self.base = self.fp.tell()-1
            self.fp.seek(self.base+self.offsets[-1])
            return

        def __repr__(self):
            return '<INDEX: size=%d>' % len(self)

        def __len__(self): # pylint: disable=E0303
            return len(self.offsets)-1

        def __getitem__(self, i):
            self.fp.seek(self.base+self.offsets[i])
            return self.fp.read(self.offsets[i+1]-self.offsets[i])

        def __iter__(self):
            return iter(self[i] for i in range(len(self)))

    def __init__(self, name, fp):
        self.name = name
        self.fp = fp
        # Header
        (_major, _minor, hdrsize, _) = struct.unpack('BBBB', self.fp.read(4))
        self.fp.read(hdrsize-4)
        # Name INDEX
        self.name_index = self.INDEX(self.fp)
        # Top DICT INDEX
        self.dict_index = self.INDEX(self.fp)
        # String INDEX
        self.string_index = self.INDEX(self.fp)
        # Global Subr INDEX
        self.subr_index = self.INDEX(self.fp)
        # Top DICT DATA
        self.top_dict = getdict(self.dict_index[0])
        (charset_pos,) = self.top_dict.get(15, [0])
        (encoding_pos,) = self.top_dict.get(16, [0])
        (charstring_pos,) = self.top_dict.get(17, [0])
        # CharStrings
        self.fp.seek(charstring_pos)
        self.charstring = self.INDEX(self.fp)
        self.nglyphs = len(self.charstring)
        # Encodings
        self.code2gid = {}
        self.gid2code = {}
        self.fp.seek(encoding_pos)
        format = self.fp.read(1)
        if format == b'\x00':
            # Format 0
            (n,) = struct.unpack('B', self.fp.read(1))
            for (code, gid) in enumerate(struct.unpack('B'*n, self.fp.read(n))):
                self.code2gid[code] = gid
                self.gid2code[gid] = code
        elif format == b'\x01':
            # Format 1
            (n,) = struct.unpack('B', self.fp.read(1))
            code = 0
            for _ in range(n):
                (first, nleft) = struct.unpack('BB', self.fp.read(2))
                for gid in range(first, first+nleft+1):
                    self.code2gid[code] = gid
                    self.gid2code[gid] = code
                    code += 1
        else:
            raise ValueError('unsupported encoding format: %r' % format)
        # Charsets
        self.name2gid = {}
        self.gid2name = {}
        self.fp.seek(charset_pos)
        format = self.fp.read(1)
        if format == b'\x00':
            # Format 0
            n = self.nglyphs-1
            for (gid, sid) in enumerate(struct.unpack('>'+'H'*n, self.fp.read(2*n))):
                gid += 1
                name = self.getstr(sid)
                self.name2gid[name] = gid
                self.gid2name[gid] = name
        elif format == b'\x01':
            # Format 1
            (n,) = struct.unpack('B', self.fp.read(1))
            sid = 0
            for _ in range(n):
                (first, nleft) = struct.unpack('BB', self.fp.read(2))
                for gid in range(first, first+nleft+1):
                    name = self.getstr(sid)
                    self.name2gid[name] = gid
                    self.gid2name[gid] = name
                    sid += 1
        elif format == b'\x02':
            # Format 2
            assert False, str(('Unhandled', format))
        else:
            raise ValueError('unsupported charset format: %r' % format)
        #print self.code2gid
        #print self.name2gid
        #assert 0
        return

    def getstr(self, sid):
        if sid < len(self.STANDARD_STRINGS):
            return self.STANDARD_STRINGS[sid]
        return self.string_index[sid-len(self.STANDARD_STRINGS)]
