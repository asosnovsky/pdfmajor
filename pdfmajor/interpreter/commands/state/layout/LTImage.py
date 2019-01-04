import os
from io import BytesIO

import PIL as pillow

from pdfmajor.BMPWriter import BMPWriter
from pdfmajor.utils import Bbox
from pdfmajor.parser.PDFStream import PDFStream, LITERALS_DCT_DECODE
from pdfmajor.parser.constants import LIT

from ._base import LTComponent

LITERAL_DEVICE_GRAY = LIT('DeviceGray')
LITERAL_DEVICE_RGB = LIT('DeviceRGB')
LITERAL_DEVICE_CMYK = LIT('DeviceCMYK')

##  LTImage
##
class LTImage(LTComponent):

    def __init__(self, name: str, stream: PDFStream, bbox: Bbox):
        LTComponent.__init__(self, bbox)
        self.name = name
        self.stream = stream
        self.srcsize = (stream.get_any(('W', 'Width')),
                        stream.get_any(('H', 'Height')))
        self.imagemask = stream.get_any(('IM', 'ImageMask'))
        self.bits = stream.get_any(('BPC', 'BitsPerComponent'), 1)
        self.colorspace = stream.get_any(('CS', 'ColorSpace'))
        if not isinstance(self.colorspace, list):
            self.colorspace = [self.colorspace]
        return

    def __repr__(self):
        return ('<%s(%s) %s %r>' %
                (self.__class__.__name__, self.name,
                 str(self.bbox), self.srcsize))
    
    def save_image(self, outdir: str, file_name: str = None):
        stream = self.stream
        filters = stream.get_filters()
        width = self.bbox.width
        height = self.bbox.height
        bits = self.bits

        if len(filters) == 1 and filters[0][0] in LITERALS_DCT_DECODE:
            ext = '.jpg'
        elif (bits == 1 or
                bits == 8 and self.colorspace in (LITERAL_DEVICE_RGB, LITERAL_DEVICE_GRAY)):
            ext = '.w%dh%d.bmp' % (width, height)
        else:
            ext = '.b%dw%dh%d.img' % (bits, width, height)

        if file_name is None:
            file_name = self.name + ext
        else:
            file_name += ext
        path = os.path.join(outdir, file_name)
        
        with open(path, 'wb') as fp:
            if ext == '.jpg':
                raw_data = stream.get_rawdata()
                if LITERAL_DEVICE_CMYK in self.colorspace:
                    ifp = BytesIO(raw_data)
                    i = pillow.Image.open(ifp)
                    i = pillow.ImageChops.invert(i)
                    i = i.convert('RGB')
                    i.save(fp, 'JPEG')
                else:
                    fp.write(raw_data)
            elif bits == 1:
                BMPWriter.write_all(fp, stream, 1, width, height, (width+7)//8)
            elif bits == 8 and self.colorspace is LITERAL_DEVICE_RGB:
                BMPWriter.write_all(fp, stream, 24, width, height, width*3)
            elif bits == 8 and self.colorspace is LITERAL_DEVICE_GRAY:
                BMPWriter.write_all(fp, stream, 8, width, height, width)
            else:
                fp.write(stream.get_data())
        return path