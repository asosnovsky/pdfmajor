from unittest import TestCase

from pdfmajor.parser.fliters.ccit import CCITTG4Parser
from pdfmajor.parser.fliters.lzw import lzwdecode
from pdfmajor.parser.fliters.rld import rldecode


class Filters(TestCase):
    def test_lzwdecode(self):
        self.assertEqual(
            lzwdecode(b"\x80\x0b\x60\x50\x22\x0c\x0c\x85\x01"),
            b"\x2d\x2d\x2d\x2d\x2d\x41\x2d\x2d\x2d\x42",
        )

    def test_rldecode(self):
        self.assertEqual(
            rldecode(b"\x05123456\xfa7\x04abcde\x80junk"), b"1234567777777abcde"
        )


class CCIT(TestCase):
    def get_parser(self, bits):
        parser = CCITTG4Parser(len(bits))
        parser._curline = [int(c) for c in bits]
        parser._reset_line()
        return parser

    def test_b1(self):
        parser = self.get_parser("00000")
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 0)
        return

    def test_b2(self):
        parser = self.get_parser("10000")
        parser._do_vertical(-1)
        self.assertEqual(parser._curpos, 0)
        return

    def test_b3(self):
        parser = self.get_parser("000111")
        parser._do_pass()
        self.assertEqual(parser._curpos, 3)
        self.assertEqual(parser._get_bits(), "111")
        return

    def test_b4(self):
        parser = self.get_parser("00000")
        parser._do_vertical(+2)
        self.assertEqual(parser._curpos, 2)
        self.assertEqual(parser._get_bits(), "11")
        return

    def test_b5(self):
        parser = self.get_parser("11111111100")
        parser._do_horizontal(0, 3)
        self.assertEqual(parser._curpos, 3)
        parser._do_vertical(1)
        self.assertEqual(parser._curpos, 10)
        self.assertEqual(parser._get_bits(), "0001111111")
        return

    def test_e1(self):
        parser = self.get_parser("10000")
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 1)
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 5)
        self.assertEqual(parser._get_bits(), "10000")
        return

    def test_e2(self):
        parser = self.get_parser("10011")
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 1)
        parser._do_vertical(2)
        self.assertEqual(parser._curpos, 5)
        self.assertEqual(parser._get_bits(), "10000")
        return

    def test_e3(self):
        parser = self.get_parser("011111")
        parser._color = 0
        parser._do_vertical(0)
        self.assertEqual(parser._color, 1)
        self.assertEqual(parser._curpos, 1)
        parser._do_vertical(-2)
        self.assertEqual(parser._color, 0)
        self.assertEqual(parser._curpos, 4)
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 6)
        self.assertEqual(parser._get_bits(), "011100")
        return

    def test_e4(self):
        parser = self.get_parser("10000")
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 1)
        parser._do_vertical(-2)
        self.assertEqual(parser._curpos, 3)
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 5)
        self.assertEqual(parser._get_bits(), "10011")
        return

    def test_e5(self):
        parser = self.get_parser("011000")
        parser._color = 0
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 1)
        parser._do_vertical(3)
        self.assertEqual(parser._curpos, 6)
        self.assertEqual(parser._get_bits(), "011111")
        return

    def test_e6(self):
        parser = self.get_parser("11001")
        parser._do_pass()
        self.assertEqual(parser._curpos, 4)
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 5)
        self.assertEqual(parser._get_bits(), "11111")
        return

    def test_e7(self):
        parser = self.get_parser("0000000000")
        parser._curpos = 2
        parser._color = 1
        parser._do_horizontal(2, 6)
        self.assertEqual(parser._curpos, 10)
        self.assertEqual(parser._get_bits(), "1111000000")
        return

    def test_e8(self):
        parser = self.get_parser("001100000")
        parser._curpos = 1
        parser._color = 0
        parser._do_vertical(0)
        self.assertEqual(parser._curpos, 2)
        parser._do_horizontal(7, 0)
        self.assertEqual(parser._curpos, 9)
        self.assertEqual(parser._get_bits(), "101111111")
        return

    def test_m1(self):
        parser = self.get_parser("10101")
        parser._do_pass()
        self.assertEqual(parser._curpos, 2)
        parser._do_pass()
        self.assertEqual(parser._curpos, 4)
        self.assertEqual(parser._get_bits(), "1111")
        return

    def test_m2(self):
        parser = self.get_parser("101011")
        parser._do_vertical(-1)
        parser._do_vertical(-1)
        parser._do_vertical(1)
        parser._do_horizontal(1, 1)
        self.assertEqual(parser._get_bits(), "011101")
        return

    def test_m3(self):
        parser = self.get_parser("10111011")
        parser._do_vertical(-1)
        parser._do_pass()
        parser._do_vertical(1)
        parser._do_vertical(1)
        self.assertEqual(parser._get_bits(), "00000001")
        return