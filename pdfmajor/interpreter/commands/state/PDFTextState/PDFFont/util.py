from pdfmajor.utils import FONT_METRICS, choplist, isnumber


def get_widths(seq):
    widths = {}
    r = []
    for v in seq:
        if isinstance(v, list):
            if r:
                char1 = r[-1]
                for (i, w) in enumerate(v):
                    widths[char1+i] = w
                r = []
        elif isnumber(v):
            r.append(v)
            if len(r) == 3:
                (char1, char2, w) = r
                for i in range(char1, char2+1):
                    widths[i] = w
                r = []
    return widths
assert get_widths([1]) == {}
assert get_widths([1,2,3]) == {1:3, 2:3}
assert get_widths([1,[2,3],6,[7,8]]) == {1:2,2:3, 6:7,7:8}

def get_widths2(seq):
    widths = {}
    r = []
    for v in seq:
        if isinstance(v, list):
            if r:
                char1 = r[-1]
                for (i, (w, vx, vy)) in enumerate(choplist(3, v)):
                    widths[char1+i] = (w, (vx, vy))
                r = []
        elif isnumber(v):
            r.append(v)
            if len(r) == 5:
                (char1, char2, w, vx, vy) = r # pylint: disable=E0632
                for i in range(char1, char2+1):
                    widths[i] = (w, (vx, vy))
                r = []
    return widths
assert get_widths2([1]) == {}
assert get_widths2([1,2,3,4,5]) == {1:(3, (4,5)), 2:(3, (4,5))}
assert get_widths2([1,[2,3,4,5],6,[7,8,9]]) == {1:(2, (3,4)), 6:(7, (8,9))}


##  FontMetricsDB
##
class FontMetricsDB(object):

    @classmethod
    def get_metrics(klass, fontname):
        return FONT_METRICS[fontname]


