import io

from decimal import Decimal
from typing import List
from unittest import TestCase

from pdfmajor.lexer import PDFLexer
from pdfmajor.lexer.exceptions import LexerError
from pdfmajor.lexer.number import parse_number
from pdfmajor.lexer.dict_and_hex import parse_double_angled_bracket, parse_hexstring
from pdfmajor.lexer.string import parse_string
from pdfmajor.lexer.name import parse_name
from pdfmajor.lexer.keyword import parse_keyword
from pdfmajor.safebufiterator import BufferStream
from pdfmajor.lexer.token import (
    TDictValue,
    Token,
    TokenBoolean,
    TokenComment,
    TokenDecimal,
    TokenDictionary,
    TokenHexString,
    TokenInteger,
    TokenKeyword,
    TokenName,
    TokenString,
)
from pdfmajor.lexer.comment import parse_comment


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
                self.assertEqual(token.value, "this % is not a comment.")
                self.assertEqual(token.end_loc, 25)

    def test_parse_string_nest_brackets(self):
        for buf_size in [1, 2, 3, 50, 100]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"x - (y*2-z-(2+3))) ", buf_size)
                token = parse_string(buffer)
                self.assertIsInstance(token, TokenString)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, "x - (y*2-z-(2+3))")
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
                self.assertEqual(token.value, "def  4ghi")
                self.assertEqual(token.end_loc, 18)

    def test_parse_string_escape_char(self):
        for buf_size in [1, 2, 3, 50, 100]:
            with self.subTest(buf_end_loc=buf_size):
                buffer = make_stream_iter(br"bach\\slask)  ", buf_size)
                token = parse_string(buffer)
                self.assertIsInstance(token, TokenString)
                self.assertEqual(token.start_loc, -1)
                self.assertEqual(token.value, r"bach\slask")
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
                self.assertEqual(token.end_loc, 2)

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
                self.assertIsInstance(token, TokenDecimal)
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
        tokenizer = PDFLexer(io.BytesIO(raw))
        for i, (etoken, token) in enumerate(zip(expected, tokenizer.iter_tokens())):
            self.assertEqual(token, etoken, f"Failed at example {i}")
        try:
            next_token = next(tokenizer.iter_tokens())
            self.assertIsNone(next_token)
        except LexerError as e:
            self.assertIsNotNone(e)

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
                TokenKeyword(start_loc=5, end_loc=5, value=b"begin"),
                TokenKeyword(start_loc=11, end_loc=3, value=b"end"),
                TokenKeyword(start_loc=16, end_loc=1, value=b'"'),
                TokenKeyword(start_loc=19, end_loc=1, value=b"@"),
                TokenKeyword(start_loc=21, end_loc=1, value=b"#"),
                TokenName(start_loc=24, end_loc=1, value="a"),
                TokenName(start_loc=26, end_loc=3, value="BCD"),
                TokenName(start_loc=31, end_loc=9, value="Some_Name"),
                TokenName(start_loc=42, end_loc=11, value="foo_naa"),
                TokenInteger(start_loc=54, end_loc=1, value=0),
                TokenInteger(start_loc=56, end_loc=2, value=1),
                TokenInteger(start_loc=59, end_loc=2, value=-2),
                TokenDecimal(start_loc=62, end_loc=2, value=Decimal("0.5")),
                TokenDecimal(start_loc=65, end_loc=5, value=Decimal("1.234")),
                TokenString(start_loc=71, end_loc=5, value="abc"),
                TokenString(start_loc=77, end_loc=2, value=""),
                TokenString(start_loc=80, end_loc=17, value="abc ( def ) ghi"),
                TokenString(start_loc=98, end_loc=19, value="def  4ghi"),
                TokenString(start_loc=118, end_loc=13, value=r"bach\slask"),
                TokenString(start_loc=132, end_loc=10, value="foo\nbaa"),
                TokenString(
                    start_loc=143, end_loc=26, value="this % is not a comment."
                ),
                TokenString(start_loc=170, end_loc=9, value="foo\nbaa"),
                TokenString(start_loc=180, end_loc=10, value="foobaa"),
                TokenHexString(start_loc=191, end_loc=2, value=b""),
                TokenHexString(start_loc=194, end_loc=4, value=b" "),
                TokenHexString(start_loc=199, end_loc=11, value=b"@@ "),
                TokenHexString(
                    start_loc=211, end_loc=14, value=b"\xab\xcd\x00\x124\x05"
                ),
                TokenKeyword(start_loc=226, end_loc=4, value=b"func"),
                TokenName(start_loc=231, end_loc=1, value="a"),
                TokenName(start_loc=233, end_loc=1, value="b"),
                TokenKeyword(start_loc=234, end_loc=1, value=b"{"),
            ],
        )

    def test_case2(self):
        self.run_test(
            raw=br"""10.32
0 +1 -2 .5 1.234
-1.234 990 """,
            expected=[
                TokenDecimal(start_loc=0, end_loc=5, value=Decimal("10.32")),
                TokenInteger(start_loc=6, end_loc=1, value=0),
                TokenInteger(start_loc=8, end_loc=2, value=1),
                TokenInteger(start_loc=11, end_loc=2, value=-2),
                TokenDecimal(start_loc=14, end_loc=2, value=Decimal("0.5")),
                TokenDecimal(start_loc=17, end_loc=5, value=Decimal("1.234")),
                TokenDecimal(start_loc=23, end_loc=6, value=Decimal("-1.234")),
                TokenInteger(start_loc=30, end_loc=3, value=990),
            ],
        )

    def test_case3(self):
        self.run_test(
            raw=br"""/b{(c)do*}def""",
            expected=[
                TokenName(start_loc=0, end_loc=2, value="b"),
                TokenKeyword(start_loc=2, end_loc=3, value=b"{"),
                TokenString(start_loc=4, end_loc=5, value="c"),
            ],
        )

    def test_case4(self):
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
                    start_loc=5, end_loc=27, value=b" This is some secret sauce"
                ),
                TokenKeyword(start_loc=33, end_loc=5, value=b"begin"),
                TokenKeyword(start_loc=39, end_loc=3, value=b"end"),
                TokenKeyword(start_loc=44, end_loc=1, value=b'"'),
                TokenKeyword(start_loc=47, end_loc=1, value=b"@"),
                TokenKeyword(start_loc=49, end_loc=1, value=b"#"),
                TokenName(start_loc=51, end_loc=2, value="a"),
                TokenName(start_loc=53, end_loc=4, value="BCD"),
                TokenName(start_loc=58, end_loc=10, value="Some_Name"),
                TokenName(start_loc=69, end_loc=12, value="foo_naa"),
                TokenName(start_loc=83, end_loc=7, value="barj"),
                TokenName(start_loc=90, end_loc=5, value="need"),
                TokenName(start_loc=96, end_loc=6, value="oh1oh"),
                TokenKeyword(start_loc=103, end_loc=4, value=b"func"),
                TokenName(start_loc=107, end_loc=3, value="a"),
                TokenName(start_loc=109, end_loc=3, value="b"),
            ],
        )
