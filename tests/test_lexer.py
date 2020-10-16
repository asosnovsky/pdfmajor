import io
from unittest import TestCase

from pdfmajor.lexer.name import parse_name
from pdfmajor.lexer.keyword import parse_keyword
from pdfmajor.safebufiterator import SafeBufferIt
from pdfmajor.lexer.token import TokenBoolean, TokenComment, TokenName
from pdfmajor.lexer.comment import parse_comment


def make_stream_iter(data: bytes, buf_size: int):
    return SafeBufferIt(io.BytesIO(data), buf_size)


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

    # def test_parse_string(self):
    #     for buf_size in [2, 3, 50, 1000]:
    #         with self.subTest(buf_end_loc=buf_size):
    #             iter_stream = make_stream_iter(br"this % is not a comment.) ", 88)
    #             token = parse_string(88, iter_stream(buf_size))
    #             self.assertIsInstance(token, TokenString)
    #             self.assertEqual(token.start_loc, 88)
    #             self.assertEqual(token.value, "this % is not a comment.")
    #             self.assertEqual(token.end_loc, 88 + 25)
