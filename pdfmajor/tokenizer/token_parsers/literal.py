
from pdfmajor.tokenizer.token_parsers.util import cmp_tsize
from pdfmajor.tokenizer.token_parsers.util import PInput
from pdfmajor.tokenizer.token import TokenLiteral
from pdfmajor.utils import int2byte
from ..constants import HEX, END_LITERAL

from typing import Iterator, NamedTuple, Optional, Union

def parse_literal(initialpos: int, inp: Iterator[PInput]) -> TokenLiteral:
	"""Parses input stream into a literal

	Args:
		initialpos (int): initial position where we started
		inp (Iterator[PInput])

	Returns:
		TokenLiteral
	"""
	curtoken = b""
	parsing_hex_mode = False
	hex_value = b""
	for curpos, s in inp:
		if parsing_hex_mode:
			hex_value, curtoken, skip_idx = _parse_literal_hex(s, hex_value, curtoken)
			if skip_idx is not None:
				curpos, s = curpos + skip_idx, s[skip_idx:]
			else:
				continue
		out = _parse_literal_raw(initialpos, curpos, s, curtoken)
		if isinstance(out, TokenLiteral):
			return out
		else:
			curtoken, parsing_hex_mode = out
			if parsing_hex_mode:
				hex_value = b""

class LiteralHexParseOut(NamedTuple):
	hex_value: bytes
	curtoken: bytes
	skip_idx: Optional[int] = None

def _parse_literal_hex(
	s: bytes, 
	hex_value: bytes, 
	curtoken: bytes
) -> LiteralHexParseOut:
	for ci in range(len(s)):
		c = s[ci:ci+1]
		if HEX.match(c) and len(hex_value) < 2:
			hex_value += c
		elif hex_value:
			curtoken += int2byte(int(hex_value, 16))
			hex_value = b""
		return LiteralHexParseOut(hex_value, curtoken, ci)
	return LiteralHexParseOut(hex_value, curtoken)

class LiteralParseOut(NamedTuple):
	curtoken: bytes
	change_to_hex_mode: bool = False

def _parse_literal_raw(
	initialpos: int, 
	curpos: int, 
	s: bytes, 
	curtoken: bytes
) -> Union[LiteralParseOut, TokenLiteral]:
	m = END_LITERAL.search(s, 0)
	if not m:
		return LiteralParseOut(curtoken+s)
	else:
		j = m.start(0)
		curtoken += s[:j]
		c = s[j : j + 1]
		if c == b"#":
			return LiteralParseOut(curtoken, True)
		curtoken = curtoken.decode()
		return TokenLiteral(
			initialpos, 
			cmp_tsize(curpos, initialpos, j), 
			curtoken
		)
