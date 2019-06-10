#!/usr/bin/env python
# -*- coding: utf-8 -*-

from  unittest import TestCase, main

#test of various compression/encoding modules (previously in doctests):
from pdfmajor.utils.ascii85 import ascii85decode, asciihexdecode
from pdfmajor.utils.lzw import LZWDecoder, lzwdecode
from pdfmajor.parser.PDFStream import rldecode

import binascii
def hex(b): return binascii.hexlify(b) #encode('hex')
def dehex(b): return binascii.unhexlify(b) #decode('hex')

class TestAscii85(TestCase):
    def test_ascii85decode(self):
        #The sample string is taken from: http://en.wikipedia.org/w/index.php?title=Ascii85
        self.assertEqual(ascii85decode(b'9jqo^BlbD-BleB1DJ+*+F(f,q'),b'Man is distinguished')
        self.assertEqual(ascii85decode(b'E,9)oF*2M7/c~>'),b'pleasure.')
        
    def test_asciihexdecode(self):
        self.assertEqual(asciihexdecode(b'61 62 2e6364   65'),b'ab.cde')
        self.assertEqual(asciihexdecode(b'61 62 2e6364   657>'),b'ab.cdep')
        self.assertEqual(asciihexdecode(b'7>'),b'p')

class TestLzw(TestCase):
    def test_lzwdecode(self):
        self.assertEqual(lzwdecode(b'\x80\x0b\x60\x50\x22\x0c\x0c\x85\x01'),b'\x2d\x2d\x2d\x2d\x2d\x41\x2d\x2d\x2d\x42')
    
class TestRunlength(TestCase):
    def test_rldecode(self):
        self.assertEqual(rldecode(b'\x05123456\xfa7\x04abcde\x80junk'),b'1234567777777abcde')
    
if __name__ == '__main__':
    main()