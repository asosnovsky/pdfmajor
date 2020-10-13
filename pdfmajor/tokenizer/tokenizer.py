
import io
from pdfmajor.tokenizer.token import TokenKeyword
from pdfmajor.tokenizer.constants import NONSPC
from typing import Iterator
from pdfmajor.tokenizer.exceptions import TokenizerEOF
from .token_parser import PInput, parse_comment, parse_number


class PSTokenizer:
	def __init__(self, fp: io.BufferedIOBase, bufsize: int = 4096) -> None:
		self.fp = fp
		self.bufsize = bufsize
		self.bufpos: int = 0
		self.buf: bytes = b''
		self.buf_skipstep: int = 0

	def iter_buffer(self) -> Iterator[PInput]:
		while True:
			if self.buf_skipstep > 0:
				yield PInput(self.bufpos + self.buf_skipstep, self.buf[self.buf_skipstep:])
				self.buf_skipstep = 0
			self.bufpos = self.fp.tell()
			self.buf = self.fp.read(self.bufsize)
			if not self.buf:
				raise TokenizerEOF("Unexpected EOF")
			else:
				yield PInput(self.bufpos, self.buf)

	def seek(self, pos: int):
		self.fp.seek(pos)	
	
	def step_back(self, steps: int = 1):
		"""Changes the offset of the stream some steps back (each step is equal to 1 self.bufsize)

		Args:
			steps (int, optional): numbers of steps. Defaults to 1.
		"""
		self.fp.seek(self.fp.tell() - steps * self.bufsize)

	def iter_tokens(self):
		for bufpos, buf in self.iter_buffer():
			m = NONSPC.search(buf, 0)
			if not m:
				self.buf_skipstep = 0
				continue
			else:
				j = m.start(0)
				c = buf[j : j + 1]
				if c == b"%":
					self.buf_skipstep = j + 1
					yield parse_comment(bufpos + j, self.iter_buffer())
				elif c == b"/":
					raise "WIP"
					# self._curtoken = b""
					# self._current_parse_func = self._parse_literal
					# return j + 1
				elif c in b"-+" or c.isdigit():
					self.buf_skipstep = j + 1
					yield parse_number(bufpos + j, self.iter_buffer(), c)
				elif c == b".":
					self.buf_skipstep = j
					yield parse_number(bufpos + j, self.iter_buffer())
				elif c.isalpha():
					raise "WIP"
					# self._curtoken = c
					# self._current_parse_func = self._parse_keyword
					# return j + 1
				elif c == b"(":
					raise "WIP"
					# self._curtoken = b""
					# self.paren = 1
					# self._current_parse_func = self._parse_string
					# return j + 1
				elif c == b"<":
					raise "WIP"
					# self._curtoken = b""
					# self._current_parse_func = self._parse_wopen
					# return j + 1
				elif c == b">":
					raise "WIP"
					# self._curtoken = b""
					# self._current_parse_func = self._parse_wclose
					# return j + 1
				else:
					self.buf_skipstep = j + 1
					yield TokenKeyword(bufpos + j, 1, c)

