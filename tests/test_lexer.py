import io
from decimal import Decimal
from typing import List
from unittest import TestCase

from pdfmajor.lexer import iter_tokens
from pdfmajor.lexer.comment import parse_comment
from pdfmajor.lexer.dict_and_hex import parse_double_angled_bracket, parse_hexstring
from pdfmajor.lexer.keyword import parse_keyword
from pdfmajor.lexer.name import parse_name
from pdfmajor.lexer.number import parse_number
from pdfmajor.lexer.string import parse_string
from pdfmajor.lexer.token import (
    TArrayValue,
    TDictValue,
    Token,
    TokenArray,
    TokenBoolean,
    TokenComment,
    TokenDictionary,
    TokenHexString,
    TokenInteger,
    TokenKeyword,
    TokenName,
    TokenNull,
    TokenReal,
    TokenString,
)
from pdfmajor.streambuffer import BufferStream


def make_stream_iter(data: bytes, buf_size: int):
    return BufferStream(io.BytesIO(data), buf_size)


class Basics(TestCase):
    def test_comment_parser_ln(self):
        for buf_size in [2, 7, 11, 150]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(
                    b"this is a lengthy comment that ends here\nso this is not reachable",
                    buf_size,
                )
                token = parse_comment(buffer)
                self.assertIsInstance(token, TokenComment)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(
                    token.value, b"this is a lengthy comment that ends here"
                )
                self.assertEqual(token.end_loc, 40)

    def test_comment_parser_lr(self):
        for buf_size in [2, 7, 11, 150]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(
                    b"this is a lengthy comment that ends here\rso this is not reachable",
                    buf_size,
                )
                token = parse_comment(buffer)
                self.assertIsInstance(token, TokenComment)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(
                    token.value, b"this is a lengthy comment that ends here"
                )
                self.assertEqual(token.end_loc, 40)

    def test_parse_bool_true(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(b"true and the american way", buf_size)
                token = parse_keyword(buffer)
                self.assertIsInstance(token, TokenBoolean)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, True)
                self.assertEqual(token.end_loc, 4)

    def test_parse_bool_false(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(b"false mannn", buf_size)
                token = parse_keyword(buffer)
                self.assertIsInstance(token, TokenBoolean)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, False)
                self.assertEqual(token.end_loc, 5)

    def test_parse_null(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(b"null Nothing here", buf_size)
                token = parse_keyword(buffer)
                self.assertIsInstance(token, TokenNull)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, None)
                self.assertEqual(token.end_loc, 4)

    def test_parse_word(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(b"likeing_turtles ", buf_size)
                token = parse_keyword(buffer)
                self.assertIsInstance(token, TokenKeyword)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, b"likeing_turtles")
                self.assertEqual(token.end_loc, 15)

    def test_parse_literal_names(self):
        for buf_size in [2, 3, 50, 444]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"Some_Name /foo#5f#xbaa", buf_size)
                token = parse_name(buffer)
                self.assertIsInstance(token, TokenName)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, "Some_Name")
                self.assertEqual(token.end_loc, 9)

    def test_parse_literal_names_hex(self):
        for buf_size in [50, 1000]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"foo#5faa ", buf_size)
                token = parse_name(buffer)
                self.assertIsInstance(token, TokenName)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, "foo_aa")
                self.assertEqual(token.end_loc, 8)

    def test_parse_string(self):
        for buf_size in [2, 3, 50, 1000]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"this % is not a comment.) ", buf_size)
                token = parse_string(buffer)
                self.assertIsInstance(token, TokenString)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, b"this % is not a comment.")
                self.assertEqual(token.end_loc, 25)

    def test_parse_string_nest_brackets(self):
        for buf_size in [1, 2, 3, 50, 100]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"x - (y*2-z-(2+3))) ", buf_size)
                token = parse_string(buffer)
                self.assertIsInstance(token, TokenString)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, b"x - (y*2-z-(2+3))")
                self.assertEqual(token.end_loc, 18)

    def test_parse_string_hex_chars(self):
        for buf_size in [1, 2, 3, 50, 100]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(
                    br"def\040\0\0404ghi) (bach\\slask)  ", buf_size
                )
                token = parse_string(buffer)
                self.assertIsInstance(token, TokenString)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, b"def  4ghi")
                self.assertEqual(token.end_loc, 18)

    def test_parse_string_escape_char(self):
        for buf_size in [1, 2, 3, 50, 100]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"bach\\slask)  ", buf_size)
                token = parse_string(buffer)
                self.assertIsInstance(token, TokenString)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, br"bach\slask")
                self.assertEqual(token.end_loc, 12)

    def test_parse_hex_string(self):
        for buf_size in [1, 2, 3, 50, 100]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"10 20 31a 12a>", buf_size)
                token = parse_hexstring(buffer)
                self.assertIsInstance(token, TokenHexString)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, b"\x10 1\xa1*")
                self.assertEqual(token.end_loc, 14)

    def test_parse_dict_keyword(self):
        for buf_size in [1, 2, 3, 50, 100]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"<wow wee", buf_size)
                token = parse_double_angled_bracket(buffer)
                self.assertIsInstance(token, TokenDictionary)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, TDictValue.OPEN)
                self.assertEqual(token.end_loc, 1)

    def test_parse_dd_to_hex(self):
        for buf_size in [1, 2, 3, 50, 100]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"10 20 31a 12a>", buf_size)
                token = parse_double_angled_bracket(buffer)
                self.assertIsInstance(token, TokenHexString)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, b"\x10 1\xa1*")
                self.assertEqual(token.end_loc, 14)

    def test_parse_float(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(b"0.120 + some invalid text", buf_size)
                token = parse_number(buffer)
                self.assertIsInstance(token, TokenReal)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, Decimal("0.12"))
                self.assertEqual(token.end_loc, 5)

    def test_parse_int(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(
                    b"130 oh oh 0.12 + some invalid text", buf_size
                )
                token = parse_number(buffer)
                self.assertIsInstance(token, TokenInteger)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, 130)
                self.assertEqual(token.end_loc, 3)


class Lexer(TestCase):
    def run_test(self, raw: bytes, expected: List[Token]):
        size = len(raw)
        for buf_size in [
            2,
            3,
            size // 4,
            size // 3,
            size // 2,
            3 * size // 4,
            size,
            2 * size,
            4 * size,
        ]:
            with self.subTest(raw=raw, buf_size=buf_size):
                it = iter_tokens(make_stream_iter(raw, buf_size))
                for i, (etoken, token) in enumerate(zip(expected, it)):
                    self.assertEqual(token, etoken, f"Failed at example #{i}")
                try:
                    next_token = next(it)
                    self.assertIsNone(next_token)
                except (EOFError, StopIteration) as e:
                    self.assertIsNotNone(e)

    def test_scase1(self):
        self.run_test(
            b"begin end\n",
            expected=[
                TokenKeyword(0, 5, b"begin"),
                TokenKeyword(6, 9, b"end"),
            ],
        )

    def test_scase2(self):
        self.run_test(
            b"/Length 4 0 R\n",
            expected=[
                TokenName(0, 7, "Length"),
                TokenInteger(8, 9, 4),
                TokenInteger(10, 11, 0),
                TokenKeyword(12, 13, b"R"),
            ],
        )

    def test_scase3(self):
        self.run_test(
            b"""endstream
endobj
4 0 obj
   2618
endobj
""",
            expected=[
                TokenKeyword(0, 9, b"endstream"),
                TokenKeyword(10, 16, b"endobj"),
                TokenInteger(17, 18, 4),
                TokenInteger(19, 20, 0),
                TokenKeyword(21, 24, b"obj"),
                TokenInteger(28, 32, 2618),
                TokenKeyword(33, 39, b"endobj"),
            ],
        )

    def test_case1(self):
        self.run_test(
            raw=br"""%!PS
begin end
 "  @ #
/a/BCD /Some_Name /foo#5f#6eaa
0 +1 -2 .5 1.234
(abc) () (abc ( def ) ghi)
(def\040\0\0404ghi) (bach\\slask) (foo\nbaa)
(this % is not a comment.)
(foo
baa)
(foo\
baa)
<> <20> < 40 4020 >
<abcd00
12345>
func/a/b{(c)do*}def
[ 1 (z) ! ]
<< /foo (bar) >>""",
            expected=[
                TokenComment(start_loc=0, end_loc=4, value=b"!PS"),
                TokenKeyword(start_loc=5, end_loc=10, value=b"begin"),
                TokenKeyword(start_loc=11, end_loc=14, value=b"end"),
                TokenKeyword(start_loc=16, end_loc=17, value=b'"'),
                TokenKeyword(start_loc=19, end_loc=20, value=b"@"),
                TokenKeyword(start_loc=21, end_loc=22, value=b"#"),
                TokenName(start_loc=23, end_loc=25, value="a"),
                TokenName(start_loc=25, end_loc=29, value="BCD"),
                TokenName(start_loc=30, end_loc=40, value="Some_Name"),
                TokenName(start_loc=41, end_loc=53, value="foo_naa"),
                TokenInteger(start_loc=54, end_loc=55, value=0),
                TokenInteger(start_loc=56, end_loc=58, value=1),
                TokenInteger(start_loc=59, end_loc=61, value=-2),
                TokenReal(start_loc=62, end_loc=64, value=Decimal("0.5")),
                TokenReal(start_loc=65, end_loc=70, value=Decimal("1.234")),
                TokenString(start_loc=71, end_loc=76, value=b"abc"),
                TokenString(start_loc=77, end_loc=79, value=b""),
                TokenString(start_loc=80, end_loc=97, value=b"abc ( def ) ghi"),
                TokenString(start_loc=98, end_loc=117, value=b"def  4ghi"),
                TokenString(start_loc=118, end_loc=131, value=br"bach\slask"),
                TokenString(start_loc=132, end_loc=142, value=b"foo\nbaa"),
                TokenString(
                    start_loc=143, end_loc=169, value=b"this % is not a comment."
                ),
                TokenString(start_loc=170, end_loc=179, value=b"foo\nbaa"),
                TokenString(start_loc=180, end_loc=190, value=b"foobaa"),
                TokenHexString(start_loc=191, end_loc=193, value=b""),
                TokenHexString(start_loc=194, end_loc=198, value=b" "),
                TokenHexString(start_loc=199, end_loc=210, value=b"@@ "),
                TokenHexString(
                    start_loc=211, end_loc=225, value=b"\xab\xcd\x00\x124\x05"
                ),
                TokenKeyword(start_loc=226, end_loc=230, value=b"func"),
                TokenName(start_loc=230, end_loc=232, value="a"),
                TokenName(start_loc=232, end_loc=234, value="b"),
                TokenKeyword(start_loc=234, end_loc=235, value=b"{"),
                TokenString(start_loc=235, end_loc=238, value=b"c"),
                TokenKeyword(start_loc=238, end_loc=241, value=b"do*"),
                TokenKeyword(start_loc=241, end_loc=242, value=b"}"),
                TokenKeyword(start_loc=242, end_loc=245, value=b"def"),
                TokenArray(start_loc=246, end_loc=247, value=TArrayValue.OPEN),
                TokenInteger(start_loc=248, end_loc=249, value=1),
                TokenString(start_loc=250, end_loc=253, value=b"z"),
                TokenKeyword(start_loc=254, end_loc=255, value=b"!"),
                TokenArray(start_loc=256, end_loc=257, value=TArrayValue.CLOSE),
                TokenDictionary(start_loc=258, end_loc=260, value=TDictValue.OPEN),
                TokenName(start_loc=261, end_loc=265, value="foo"),
                TokenString(start_loc=266, end_loc=271, value=b"bar"),
                TokenDictionary(start_loc=273, end_loc=275, value=TDictValue.CLOSE),
            ],
        )

    def test_case2(self):
        self.run_test(
            raw=br"""10.32
0 +1 -2 .5 1.234
-1.234 990 """,
            expected=[
                TokenReal(start_loc=0, end_loc=5, value=Decimal("10.32")),
                TokenInteger(start_loc=6, end_loc=7, value=0),
                TokenInteger(start_loc=8, end_loc=10, value=1),
                TokenInteger(start_loc=11, end_loc=13, value=-2),
                TokenReal(start_loc=14, end_loc=16, value=Decimal("0.5")),
                TokenReal(start_loc=17, end_loc=22, value=Decimal("1.234")),
                TokenReal(start_loc=23, end_loc=29, value=Decimal("-1.234")),
                TokenInteger(start_loc=30, end_loc=33, value=990),
            ],
        )

    def test_case3(self):
        self.run_test(
            raw=br"""%!PS
% This is some secret sauce
begin end
 "  @ #
/a/BCD /Some_Name /foo#5f#6eaa /bar#6a
/need /oh1oh
func/a/b
""",
            expected=[
                TokenComment(start_loc=0, end_loc=4, value=b"!PS"),
                TokenComment(
                    start_loc=5, end_loc=32, value=b" This is some secret sauce"
                ),
                TokenKeyword(start_loc=33, end_loc=38, value=b"begin"),
                TokenKeyword(start_loc=39, end_loc=42, value=b"end"),
                TokenKeyword(start_loc=44, end_loc=45, value=b'"'),
                TokenKeyword(start_loc=47, end_loc=48, value=b"@"),
                TokenKeyword(start_loc=49, end_loc=50, value=b"#"),
                TokenName(start_loc=51, end_loc=53, value="a"),
                TokenName(start_loc=53, end_loc=57, value="BCD"),
                TokenName(start_loc=58, end_loc=68, value="Some_Name"),
                TokenName(start_loc=69, end_loc=81, value="foo_naa"),
                TokenName(start_loc=82, end_loc=89, value="barj"),
                TokenName(start_loc=90, end_loc=95, value="need"),
                TokenName(start_loc=96, end_loc=102, value="oh1oh"),
                TokenKeyword(start_loc=103, end_loc=107, value=b"func"),
                TokenName(start_loc=107, end_loc=109, value="a"),
                TokenName(start_loc=109, end_loc=111, value="b"),
            ],
        )
