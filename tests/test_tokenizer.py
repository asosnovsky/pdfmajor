from decimal import Decimal
import io
from typing import List
from pdfmajor.tokenizer.token_parsers.string import parse_string
from pdfmajor.tokenizer import PSTokenizer
from pdfmajor.tokenizer.token import (
    Token,
    TokenBoolean,
    TokenComment,
    TokenDecimal,
    TokenInteger,
    TokenKeyword,
    TokenLiteral,
    TokenString,
)
from pdfmajor.tokenizer.token_parsers.util import PInput
from pdfmajor.tokenizer.token_parsers.comment import parse_comment
from pdfmajor.tokenizer.token_parsers.keyword import parse_keyword
from pdfmajor.tokenizer.token_parsers.number import parse_number
from pdfmajor.tokenizer.token_parsers.literal import parse_literal
from unittest import TestCase


def make_stream_iter(data: bytes, initpos: int = 0):
    stream = io.BytesIO(data)

    def iter_stream(buf_size: int):
        while True:
            bufpos = stream.tell()
            buf = stream.read(buf_size)
            if buf:
                yield PInput(initpos + bufpos, buf)
            else:
                raise "EOF"

    return iter_stream


class Individual(TestCase):
    def test_comment_parser_ln(self):
        for buf_size in [2, 7, 11, 150]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(
                    b"this is a lengthy comment that ends here\nso this is not reachable"
                )
                token = parse_comment(0, iter_stream(buf_size))
                self.assertIsInstance(token, TokenComment)
                self.assertEqual(token.pos, 0)
                self.assertEqual(
                    token.value, b"this is a lengthy comment that ends here"
                )
                self.assertEqual(token.size, 40)

    def test_comment_parser_lr(self):
        for buf_size in [2, 7, 11, 150]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(
                    b"this is a lengthy comment that ends here\rso this is not reachable"
                )
                token = parse_comment(0, iter_stream(buf_size))
                self.assertIsInstance(token, TokenComment)
                self.assertEqual(token.pos, 0)
                self.assertEqual(
                    token.value, b"this is a lengthy comment that ends here"
                )
                self.assertEqual(token.size, 40)

    def test_parse_float(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(b"0.120 + some invalid text", 5)
                token = parse_number(5, iter_stream(buf_size))
                self.assertIsInstance(token, TokenDecimal)
                self.assertEqual(token.pos, 5)
                self.assertEqual(token.value, Decimal("0.12"))
                self.assertEqual(token.size, 5)

    def test_parse_int(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(
                    b"130 oh oh 0.12 + some invalid text", 11
                )
                token = parse_number(11, iter_stream(buf_size))
                self.assertIsInstance(token, TokenInteger)
                self.assertEqual(token.pos, 11)
                self.assertEqual(token.value, 130)
                self.assertEqual(token.size, 3)

    def test_parse_bool_true(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(b"true and the american way", 91)
                token = parse_keyword(91, iter_stream(buf_size))
                self.assertIsInstance(token, TokenBoolean)
                self.assertEqual(token.pos, 91)
                self.assertEqual(token.value, True)
                self.assertEqual(token.size, 4)

    def test_parse_bool_false(self):
        for buf_size in [2, 3, 50]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(b"false mannn", 33)
                token = parse_keyword(33, iter_stream(buf_size))
                self.assertIsInstance(token, TokenBoolean)
                self.assertEqual(token.pos, 33)
                self.assertEqual(token.value, False)
                self.assertEqual(token.size, 5)

    def test_parse_literals(self):
        for buf_size in [2, 3, 50, 444]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(br"Some_Name /foo#5f#xbaa", 71)
                token = parse_literal(71, iter_stream(buf_size))
                self.assertIsInstance(token, TokenLiteral)
                self.assertEqual(token.pos, 71)
                self.assertEqual(token.value, "Some_Name")
                self.assertEqual(token.size, 9)

    def test_parse_literals_hex(self):
        for buf_size in [2]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(br"foo#5faa ", 71)
                token = parse_literal(71, iter_stream(buf_size))
                self.assertIsInstance(token, TokenLiteral)
                self.assertEqual(token.pos, 71)
                self.assertEqual(token.value, "foo_aa")
                self.assertEqual(token.size, 8)

    def test_parse_string(self):
        for buf_size in [2]:
            with self.subTest(buf_size=buf_size):
                iter_stream = make_stream_iter(br"this % is not a comment.) ", 88)
                token = parse_string(88, iter_stream(buf_size))
                self.assertIsInstance(token, TokenString)
                self.assertEqual(token.pos, 88)
                self.assertEqual(token.value, "this % is not a comment.")
                self.assertEqual(token.size, 24)


class Tokenizer(TestCase):
    def run_test(self, raw: bytes, expected: List[Token]):
        tokenizer = PSTokenizer(io.BytesIO(raw))
        for i, (etoken, token) in enumerate(zip(expected, tokenizer.iter_tokens())):
            self.assertEqual(token, etoken, f"Failed at example {i}")

    def test_case1(self):
        tokenizer = PSTokenizer(
            io.BytesIO(
                br"""%!PS
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
<< /foo (bar) >>"""
            )
        )
        for token in tokenizer.iter_tokens():
            print(token)

    def test_case2(self):
        self.run_test(
            raw=br"""10.32
0 +1 -2 .5 1.234
-1.234 990""",
            expected=[
                TokenDecimal(pos=0, size=5, value=Decimal("10.32")),
                TokenInteger(pos=6, size=1, value=0),
                TokenInteger(pos=8, size=2, value=1),
                TokenInteger(pos=11, size=2, value=-2),
                TokenDecimal(pos=14, size=2, value=Decimal("0.5")),
                TokenDecimal(pos=17, size=5, value=Decimal("1.234")),
                TokenDecimal(pos=23, size=6, value=Decimal("-1.234")),
                TokenInteger(pos=30, size=3, value=990),
            ],
        )

    def test_case_words1(self):
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
                TokenComment(pos=0, size=4, value=b"!PS"),
                TokenComment(pos=5, size=27, value=b" This is some secret sauce"),
                TokenKeyword(pos=33, size=5, value=b"begin"),
                TokenKeyword(pos=39, size=3, value=b"end"),
                TokenKeyword(pos=44, size=1, value=b'"'),
                TokenKeyword(pos=47, size=1, value=b"@"),
                TokenKeyword(pos=49, size=1, value=b"#"),
                TokenLiteral(pos=52, size=1, value="a"),
                TokenLiteral(pos=54, size=3, value="BCD"),
                TokenLiteral(pos=59, size=9, value="Some_Name"),
                TokenLiteral(pos=70, size=11, value="foo_naa"),
                TokenLiteral(pos=83, size=6, value="barj"),
                TokenLiteral(pos=91, size=4, value="need"),
                TokenLiteral(pos=97, size=5, value="oh1oh"),
                TokenKeyword(pos=103, size=4, value=b"func"),
                TokenLiteral(pos=108, size=1, value="a"),
                TokenLiteral(pos=110, size=1, value="b"),
            ],
        )
