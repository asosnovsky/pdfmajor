import struct
import chardet  

# from sys import maxint as INF #doesn't work anymore under Python3,
# but PDF still uses 32 bits ints
int2byte = struct.Struct(">B").pack

def make_compat_bytes(in_str):
    "In Py2, does nothing. In Py3, converts to bytes, encoding to unicode."
    assert isinstance(in_str, str), str(type(in_str))
    return in_str.encode()

def make_compat_str(in_str):
    "In Py2, does nothing. In Py3, converts to string, guessing encoding."
    assert isinstance(in_str, (bytes, str, unicode)), str(type(in_str))
    if isinstance(in_str, bytes):
        enc = chardet.detect(in_str)
        in_str = in_str.decode(enc['encoding'])
    return in_str

def compatible_encode_method(bytesorstring, encoding='utf-8', erraction='ignore'):
    if isinstance(bytesorstring, str): return bytesorstring
    assert isinstance(bytesorstring, bytes), str(type(bytesorstring))
    return bytesorstring.decode(encoding, erraction)

##  PNG Predictor
##
def apply_png_predictor(pred, colors, columns, bitspercomponent, data):
    if bitspercomponent != 8:
        # unsupported
        raise ValueError("Unsupported `bitspercomponent': %d" %
                         bitspercomponent)
    nbytes = colors * columns * bitspercomponent // 8
    i = 0
    buf = b''
    line0 = b'\x00' * columns
    for i in range(0, len(data), nbytes+1):
        ft = data[i]
        i += 1
        line1 = data[i:i+nbytes]
        line2 = b''
        if ft == 0:
            # PNG none
            line2 += line1
        elif ft == 1:
            # PNG sub (UNTESTED)
            c = 0
            for b in line1:
                c = (c+b) & 255
                line2 += int2byte(c)
        elif ft == 2:
            # PNG up
            for (a, b) in zip(line0, line1):
                c = (a+b) & 255
                line2 += int2byte(c)
        elif ft == 3:
            # PNG average (UNTESTED)
            c = 0
            for (a, b) in zip(line0, line1):
                c = ((c+a+b)//2) & 255
                line2 += int2byte(c)
        else:
            # unsupported
            raise ValueError("Unsupported predictor value: %d" % ft)
        buf += line2
        line0 = line2
    return buf




##  Utility functions
##

# isnumber
def isnumber(x):
    return isinstance(x, (int, float))

# uniq
def uniq(objs):
    """Eliminates duplicated elements."""
    done = set()
    for obj in objs:
        if obj in done:
            continue
        done.add(obj)
        yield obj
    return


# csort
def csort(objs, key):
    """Order-preserving sorting function."""
    idxs = dict((obj, i) for (i, obj) in enumerate(objs))
    return sorted(objs, key=lambda obj: (key(obj), idxs[obj]))


# drange
def drange(v0, v1, d):
    """Returns a discrete range."""
    assert v0 < v1, str((v0, v1, d))
    return range(int(v0)//d, int(v1+d)//d)

# pick
def pick(seq, func, maxobj=None):
    """Picks the object obj where func(obj) has the highest value."""
    maxscore = None
    for obj in seq:
        score = func(obj)
        if maxscore is None or maxscore < score:
            (maxscore, maxobj) = (score, obj)
    return maxobj


# choplist
def choplist(n, seq):
    """Groups every n elements of the list."""
    r = []
    for x in seq:
        r.append(x)
        if len(r) == n:
            yield tuple(r)
            r = []
    return


# nunpack
def nunpack(s, default=0):
    """Unpacks 1 to 4 or 8 byte integers (big endian)."""
    l = len(s)
    if not l:
        return default
    elif l == 1:
        return ord(s)
    elif l == 2:
        return struct.unpack('>H', s)[0]
    elif l == 3:
        return struct.unpack('>L', b'\x00'+s)[0]
    elif l == 4:
        return struct.unpack('>L', s)[0]
    elif l == 8:
        return struct.unpack('>Q', s)[0]
    else:
        raise TypeError('invalid length: %d' % l)

##  Plane
##
##  A set-like data structure for objects placed on a plane.
##  Can efficiently find objects in a certain rectangular area.
##  It maintains two parallel lists of objects, each of
##  which is sorted by its x or y coordinate.
##
class Plane(object):

    def __init__(self, bbox, gridsize=50):
        self._seq = []          # preserve the object order.
        self._objs = set()
        self._grid = {}
        self.gridsize = gridsize
        (self.x0, self.y0, self.x1, self.y1) = bbox
        return

    def __repr__(self):
        return ('<Plane objs=%r>' % list(self))

    def __iter__(self):
        return ( obj for obj in self._seq if obj in self._objs )

    def __len__(self):
        return len(self._objs)

    def __contains__(self, obj):
        return obj in self._objs

    def _getrange(self, bbox):
        (x0, y0, x1, y1) = bbox
        if (x1 <= self.x0 or self.x1 <= x0 or
            y1 <= self.y0 or self.y1 <= y0): return
        x0 = max(self.x0, x0)
        y0 = max(self.y0, y0)
        x1 = min(self.x1, x1)
        y1 = min(self.y1, y1)
        for y in drange(y0, y1, self.gridsize):
            for x in drange(x0, x1, self.gridsize):
                yield (x, y)
        return

    # extend(objs)
    def extend(self, objs):
        for obj in objs:
            self.add(obj)
        return

    # add(obj): place an object.
    def add(self, obj):
        for k in self._getrange((obj.x0, obj.y0, obj.x1, obj.y1)):
            if k not in self._grid:
                r = []
                self._grid[k] = r
            else:
                r = self._grid[k]
            r.append(obj)
        self._seq.append(obj)
        self._objs.add(obj)
        return

    # remove(obj): displace an object.
    def remove(self, obj):
        for k in self._getrange((obj.x0, obj.y0, obj.x1, obj.y1)):
            try:
                self._grid[k].remove(obj)
            except (KeyError, ValueError):
                pass
        self._objs.remove(obj)
        return

    # find(): finds objects that are in a certain area.
    def find(self, bbox):
        (x0, y0, x1, y1) = bbox
        done = set()
        for k in self._getrange(bbox):
            if k not in self._grid:
                continue
            for obj in self._grid[k]:
                if obj in done:
                    continue
                done.add(obj)
                if (obj.x1 <= x0 or x1 <= obj.x0 or
                    obj.y1 <= y0 or y1 <= obj.y0):
                    continue
                yield obj
        return




