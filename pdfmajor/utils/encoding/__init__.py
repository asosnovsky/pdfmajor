import re
from .glyphlist import glyphname2unicode
from .latin_enc import LATIN_ENCODING

STRIP_NAME = re.compile(r'[0-9]+')

##  name2unicode
##
def name2unicode(name):
    """Converts Adobe glyph names to Unicode numbers."""
    if name in glyphname2unicode:
        return glyphname2unicode[name]
    m = STRIP_NAME.search(name)
    if not m:
        raise KeyError(name)
    return chr(int(m.group(0)))

