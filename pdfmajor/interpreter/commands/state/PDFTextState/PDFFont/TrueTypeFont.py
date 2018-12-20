##  TrueTypeFont
##
import struct
from pdfmajor.parser.cmapdb import FileUnicodeMap

class TrueTypeFont(object):

    class CMapNotFound(Exception):
        pass

    def __init__(self, name, fp):
        self.name = name
        self.fp = fp
        self.tables = {}
        self.fonttype = fp.read(4)
        try:
            (ntables, _1, _2, _3) = struct.unpack('>HHHH', fp.read(8))
            for _ in range(ntables):
                (name, _, offset, length) = struct.unpack('>4sLLL', fp.read(16))
                self.tables[name] = (offset, length)
        except struct.error:
            # Do not fail if there are not enough bytes to read. Even for
            # corrupted PDFs we would like to get as much information as
            # possible, so continue.
            pass
        return

    def create_unicode_map(self):
        if 'cmap' not in self.tables:
            raise TrueTypeFont.CMapNotFound
        (base_offset, _) = self.tables['cmap']
        fp = self.fp
        fp.seek(base_offset)
        (_, nsubtables) = struct.unpack('>HH', fp.read(4))
        subtables = []
        for i in range(nsubtables):
            subtables.append(struct.unpack('>HHL', fp.read(8)))
        char2gid = {}
        # Only supports subtable type 0, 2 and 4.
        for (_1, _2, st_offset) in subtables:
            fp.seek(base_offset+st_offset)
            (fmttype, _, _) = struct.unpack('>HHH', fp.read(6))
            if fmttype == 0:
                char2gid.update(enumerate(struct.unpack('>256B', fp.read(256))))
            elif fmttype == 2:
                subheaderkeys = struct.unpack('>256H', fp.read(512))
                firstbytes = [0]*8192
                for (i, k) in enumerate(subheaderkeys):
                    firstbytes[k//8] = i
                nhdrs = max(subheaderkeys)//8 + 1
                hdrs = []
                for i in range(nhdrs):
                    (firstcode, entcount, delta, offset) = struct.unpack('>HHhH', fp.read(8))
                    hdrs.append((i, firstcode, entcount, delta, fp.tell()-2+offset))
                for (i, firstcode, entcount, delta, pos) in hdrs:
                    if not entcount:
                        continue
                    first = firstcode + (firstbytes[i] << 8)
                    fp.seek(pos)
                    for c in range(entcount):
                        gid = struct.unpack('>H', fp.read(2))
                        if gid:
                            gid += delta
                        char2gid[first+c] = gid
            elif fmttype == 4:
                (segcount, _1, _2, _3) = struct.unpack('>HHHH', fp.read(8))
                segcount //= 2
                ecs = struct.unpack('>%dH' % segcount, fp.read(2*segcount))
                fp.read(2)
                scs = struct.unpack('>%dH' % segcount, fp.read(2*segcount))
                idds = struct.unpack('>%dh' % segcount, fp.read(2*segcount))
                pos = fp.tell()
                idrs = struct.unpack('>%dH' % segcount, fp.read(2*segcount))
                for (ec, sc, idd, idr) in zip(ecs, scs, idds, idrs):
                    if idr:
                        fp.seek(pos+idr)
                        for c in range(sc, ec+1):
                            char2gid[c] = (struct.unpack('>H', fp.read(2))[0] + idd) & 0xffff
                    else:
                        for c in range(sc, ec+1):
                            char2gid[c] = (c + idd) & 0xffff
            else:
                assert False, str(('Unhandled', fmttype))
        # create unicode map
        unicode_map = FileUnicodeMap()
        for (char, gid) in char2gid.items():
            unicode_map.add_cid2unichr(gid, char)
        return unicode_map

