from decimal import Decimal
import io
from pdfmajor.tokenizer.token import TokenComment, TokenDecimal, TokenInteger
from pdfmajor.tokenizer.token_parser import PInput, parse_comment, parse_number
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


