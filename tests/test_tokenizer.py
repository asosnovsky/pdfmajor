from decimal import Decimal
import io
from pdfmajor.tokenizer.token import TokenBoolean, TokenComment, TokenDecimal, TokenInteger, TokenLiteral
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
				yield PInput(initpos+bufpos, buf)
			else:
				raise "EOF"
	return iter_stream

class Basics(TestCase):
	def test_comment_parser_ln(self):
		iter_stream = make_stream_iter(
			b"this is a lengthy comment that ends here\nso this is not reachable"
		)
		token = parse_comment(0, iter_stream(3))
		self.assertIsInstance(token, TokenComment)
		self.assertEqual(token.pos, 0)
		self.assertEqual(token.value, b"this is a lengthy comment that ends here")
		self.assertEqual(token.size, 40)

	def test_comment_parser_lr(self):
		iter_stream = make_stream_iter(
			b"this is a lengthy comment that ends here\rso this is not reachable"
		)
		token = parse_comment(0, iter_stream(7))
		self.assertIsInstance(token, TokenComment)
		self.assertEqual(token.pos, 0)
		self.assertEqual(token.value, b"this is a lengthy comment that ends here")
		self.assertEqual(token.size, 40)

	def test_parse_float(self):
		iter_stream = make_stream_iter(
			b"0.120 + some invalid text",
			5
		)
		token = parse_number(5, iter_stream(3))
		self.assertIsInstance(token, TokenDecimal)
		self.assertEqual(token.pos, 5)
		self.assertEqual(token.value, Decimal('0.12'))
		self.assertEqual(token.size, 5)


	def test_parse_int(self):
		iter_stream = make_stream_iter(
			b"130 oh oh 0.12 + some invalid text",
			11
		)
		token = parse_number(11, iter_stream(10))
		self.assertIsInstance(token, TokenInteger)
		self.assertEqual(token.pos, 11)
		self.assertEqual(token.value, 130)
		self.assertEqual(token.size, 3)


	def test_parse_bool_true(self):
		iter_stream = make_stream_iter(
			b"true and the american way",
			91
		)
		token = parse_keyword(91, iter_stream(33))
		self.assertIsInstance(token, TokenBoolean)
		self.assertEqual(token.pos, 91)
		self.assertEqual(token.value, True)
		self.assertEqual(token.size, 4)

	def test_parse_bool_false(self):
		iter_stream = make_stream_iter(
			b"false mannn",
			33
		)
		token = parse_keyword(33, iter_stream(100))
		self.assertIsInstance(token, TokenBoolean)
		self.assertEqual(token.pos, 33)
		self.assertEqual(token.value, False)
		self.assertEqual(token.size, 5)

	def test_parse_literals(self):
		iter_stream = make_stream_iter(
			b"Some_Name /foo#5f#xbaa",
			71
		)
		token = parse_literal(71, iter_stream(1))
		self.assertIsInstance(token, TokenLiteral)
		self.assertEqual(token.pos, 71)
		self.assertEqual(token.value, 'Some_Name')
		self.assertEqual(token.size, 9)
