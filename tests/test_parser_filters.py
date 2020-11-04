from unittest import TestCase

from pdfmajor.document.parse_context import PDFParsingContext
from pdfmajor.filters.ccit import CCITTG4Parser
from pdfmajor.filters.lzw import lzwdecode
from pdfmajor.filters.rld import rldecode
from pdfmajor.pdf_parser.objects.ref import ObjectRef
from tests.util import all_pdf_files


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
        parser._curline = [int(c) for c in bits]  # type: ignore
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


class Stream(TestCase):
    def test_flatedecode(self):
        with all_pdf_files["bad-unicode.pdf"].get_window() as buffer:
            pctx = PDFParsingContext(buffer)
            stream_def, stream_data = pctx.validated_and_iter_stream(ObjectRef(161, 0))
            self.assertListEqual(
                stream_data.strip().split(b"\n"),
                [
                    b"/GS1 gs",
                    b"BT",
                    b"/TT2 1 Tf",
                    b"9.9856 0 0 9.9856 39.9 724.5601 Tm",
                    b"0 g",
                    b"0.0022 Tc",
                    b"-0.0036 Tw",
                    b"[(Map Un)-5.9(i)9.6(t)-1.3( Expla)5.6(n)-5.9(ation)6.2( )]TJ",
                    b"7.9885 0 0 7.9885 171.96 723.48 Tm",
                    b"-0.0019 Tc",
                    b"0.0095 Tw",
                    b"[(Legend: Map )15(Un)-6.9(its )7.5(for Tonto )7.5(National)-9.5( )15(Fore)-9.1(s)6(t G)9.8(e)-1.5(ol)-9.5(ogy)]TJ",
                    b"/TT4 1 Tf",
                    b"9.9856 0 0 9.9856 90.9 703.62 Tm",
                    b"0.0031 Tc",
                    b"0 Tw",
                    b"(Water)Tj",
                    b"/TT6 1 Tf",
                    b"7.9885 0 0 7.9885 108.96 690.48 Tm",
                    b"-0.0029 Tc",
                    b"[(Wat)-3(e)-2.2(r)]TJ",
                    b"ET",
                    b"/Cs6 cs 0 0.74902 1 scn",
                    b"42.48 693.66 44.04 19.98 re",
                    b"f",
                    b"BT",
                    b"/TT4 1 Tf",
                    b"13.9798 0 0 13.9798 59.52 700.26 Tm",
                    b"0 g",
                    b"0 Tc",
                    b"(w)Tj",
                    b"ET",
                    b"41.52 713.64 46.02 0.95996 re",
                    b"f",
                    b"86.52 692.64 1.02 21.96 re",
                    b"f",
                    b"41.52 692.64 46.02 1.02 re",
                    b"f",
                    b"41.52 692.64 0.95999 21.96 re",
                    b"f",
                    b"BT",
                    b"9.9856 0 0 9.9856 90.9 671.28 Tm",
                    b"0.0027 Tc",
                    b"-0.0063 Tw",
                    b"[(Dist)-6.8(u)6.1(r)-4.1(be)7.9(d)-6( g)-8(r)1.9(ound )-6(\\(rece)7.9(n)0(t\\))]TJ",
                    b"/TT6 1 Tf",
                    b"7.9885 0 0 7.9885 108.96 658.2001 Tm",
                    b"0.0031 Tc",
                    b"-0.0052 Tw",
                    b"[(H)11.7(e)-3.7(avily)7.4( distur)5.6(bed gr)5.6(ound)-7.6( )7.6(d)-7.6(u)7.4(e to)7.4( )-7.5(ag)7.4(ri)10.5(cu)7.4(lt)10.5(u)-7.6(r)13.1(e,)5.2( )7.6(exte)]TJ",
                    b"19.7159 0 TD",
                    b"0.002 Tc",
                    b"0.0034 Tw",
                    b"[(nsive )7.5(excavation,)4.1( o)6.3(r)4.5( )7.5(co)-8.7(n)6.3(s)0.6(tr)4.5(uct)9.4(i)-5.6(on)6.3( o)6.3(f)-3( ear)12(th )7.5(dam)21.2(s)]TJ",
                    b"ET",
                    b"0.82 g",
                    b"42.48 661.32 44.04 19.98 re",
                    b"f",
                    b"BT",
                    b"/TT4 1 Tf",
                    b"13.9798 0 0 13.9798 60.6 667.92 Tm",
                    b"0 g",
                    b"0 Tc",
                    b"0 Tw",
                    b"(d)Tj",
                    b"ET",
                    b"41.52 681.3 46.02 1.02 re",
                    b"f",
                    b"86.52 660.36 1.02 21.96 re",
                    b"f",
                    b"41.52 660.36 46.02 0.96002 re",
                    b"f",
                    b"41.52 660.36 0.95999 21.96 re",
                    b"f",
                    b"BT",
                    b"9.9856 0 0 9.9856 90.9 639 Tm",
                    b"0.0018 Tc",
                    b"0.0006 Tw",
                    b"[(Q)-7.5(u)-0.9(at)-7.7(e)7(r)-5(nar)7(y)-8.9( sediment)-7.7(ary dep)5.2(o)-2.9(sit)-7.7(s)]TJ",
                    b"/TT6 1 Tf",
                    b"7.9885 0 0 7.9885 108.96 625.92 Tm",
                    b"0.0005 Tc",
                    b"-0.0026 Tw",
                    b"[(T)10.5(y)4.8(p)-10.2(i)0.4(cally)4.8( non m)19.7(a)1.2(rine clas)-8.4(t)7.9(i)0.4(c sedi)-7.1(m)27.2(e)-6.3(n)4.8(t)-7.1(a)8.7(r)3(y)4.8( )-7.5(rock)4.8(s)-8.4( )7.6(d)-10.2(e)1.2(posited in late P)-6.7(l)7.9(ioc)-6.3(e)8.7(n)-10.2(e)1.2( )7.6(t)-7.1(o)4.8( )-7.5(Qu)4.8(a)-6.3(t)7.9(ern)4.8(a)-6.3(ry)4.8( tim)19.7(e, in deposition)-10.2(a)8.7(l sy)4.8(st)-7.1(em)19.7(s)6.6( )-7.5(re)8.7(fl)-7.1(ec)8.7(t)-7.1(e)1.2(d)]TJ",
                    b"50.7958 0 TD",
                    b"0.0012 Tc",
                    b"-0.0033 Tw",
                    b"[( in)5.5( )-7.5(t)8.6(h)-9.5(e m)20.4(oder)3.7(n)-2( )]TJ",
                    b"-50.7958 -1.1792 TD",
                ],
            )
            self.assertDictEqual(
                stream_def.to_python(), {"Length": 1009, "Filter": "/FlateDecode"}
            )
