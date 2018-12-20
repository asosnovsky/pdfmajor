from .PDFObjRef import PDFObjRef
from ...utils import settings, isnumber, int2byte
from .exceptions import PDFTypeError

from logging import getLogger

log = getLogger(__name__)

# resolve
def resolve1(x, default=None):
    """Resolves an object.

    If this is an array or dictionary, it may still contains
    some indirect objects inside.
    """
    while isinstance(x, PDFObjRef):
        x = x.resolve(default=default)
    return x


def resolve_all(x, default=None):
    """Recursively resolves the given object and all the internals.

    Make sure there is no indirect reference within the nested object.
    This procedure might be slow.
    """
    while isinstance(x, PDFObjRef):
        x = x.resolve(default=default)
    if isinstance(x, list):
        x = [resolve_all(v, default=default) for v in x]
    elif isinstance(x, dict):
        for (k, v) in x.iteritems():
            x[k] = resolve_all(v, default=default)
    return x


def decipher_all(decipher, objid, genno, x):
    """Recursively deciphers the given object.
    """
    if isinstance(x, bytes):
        return decipher(objid, genno, x)
    if isinstance(x, list):
        x = [decipher_all(decipher, objid, genno, v) for v in x]
    elif isinstance(x, dict):
        for (k, v) in x.items():
            x[k] = decipher_all(decipher, objid, genno, v)
    return x
# Type cheking
def int_value(x):
    x = resolve1(x)
    if not isinstance(x, int):
        if settings.STRICT:
            raise PDFTypeError('Integer required: %r' % x)
        return 0
    return x


def float_value(x):
    x = resolve1(x)
    if not isinstance(x, float):
        if settings.STRICT:
            raise PDFTypeError('Float required: %r' % x)
        return 0.0
    return x


def num_value(x):
    x = resolve1(x)
    if not isnumber(x):
        if settings.STRICT:
            raise PDFTypeError('Int or Float required: %r' % x)
        return 0
    return x


def str_value(x):
    x = resolve1(x)
    if not isinstance(x, bytes):
        if settings.STRICT:
            raise PDFTypeError('String required: %r' % x)
        return ''
    return x


def list_value(x):
    x = resolve1(x)
    if not isinstance(x, (list, tuple)):
        if settings.STRICT:
            raise PDFTypeError('List required: %r' % x)
        return []
    return x


def dict_value(x):
    x = resolve1(x)
    if not isinstance(x, dict):
        if settings.STRICT:
            log.error('PDFTypeError : Dict required: %r', x)
            raise PDFTypeError('Dict required: %r' % x)
        return {}
    return x
    
#
# RunLength decoder (Adobe version) implementation based on PDF Reference
# version 1.4 section 3.3.4.
#
#  * public domain *
#
def rldecode(data):
    """
    RunLength decoder (Adobe version) implementation based on PDF Reference
    version 1.4 section 3.3.4:
        The RunLengthDecode filter decodes data that has been encoded in a
        simple byte-oriented format based on run length. The encoded data
        is a sequence of runs, where each run consists of a length byte
        followed by 1 to 128 bytes of data. If the length byte is in the
        range 0 to 127, the following length + 1 (1 to 128) bytes are
        copied literally during decompression. If length is in the range
        129 to 255, the following single byte is to be copied 257 - length
        (2 to 128) times during decompression. A length value of 128
        denotes EOD.
    """
    decoded = b''
    i = 0
    while i < len(data):
        length = data[i]
        if length == 128:
            break
        if length >= 0 and length < 128:
            for j in range(i+1,(i+1)+(length+1)):
                decoded+=int2byte(data[j])
            
            i = (i+1) + (length+1)
        if length > 128:
            run = int2byte(data[i+1])*(257-length)
            decoded+=run
            i = (i+1) + 1
    return decoded

