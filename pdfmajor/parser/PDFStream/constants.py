from ...utils import settings
from ..PSStackParser import LIT

LITERAL_CRYPT = LIT('Crypt')

# Abbreviation of Filter names in PDF 4.8.6. "Inline Images"
LITERALS_FLATE_DECODE = (LIT('FlateDecode'), LIT('Fl'))
LITERALS_LZW_DECODE = (LIT('LZWDecode'), LIT('LZW'))
LITERALS_ASCII85_DECODE = (LIT('ASCII85Decode'), LIT('A85'))
LITERALS_ASCIIHEX_DECODE = (LIT('ASCIIHexDecode'), LIT('AHx'))
LITERALS_RUNLENGTH_DECODE = (LIT('RunLengthDecode'), LIT('RL'))
LITERALS_CCITTFAX_DECODE = (LIT('CCITTFaxDecode'), LIT('CCF'))
LITERALS_DCT_DECODE = (LIT('DCTDecode'), LIT('DCT'))