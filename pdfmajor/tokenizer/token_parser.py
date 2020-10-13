from decimal import Decimal
from pdfmajor.tokenizer.exceptions import InvalidToken
from pdfmajor.tokenizer.token import Token, TokenComment, TokenDecimal, TokenNumber, TokenInteger
from pdfmajor.tokenizer.constants import END_NUMBER, EOL
from typing import Callable, Iterator, NamedTuple


class PInput(NamedTuple):
	pos: int
	buf: bytes


ParserFunc = Callable[[int, Iterator[PInput]], Token]

def cmp_tsize(curpos: int, initialpos: int, tokenend_idx: int) -> int:
	"""Computes the size of the token based on its positional data

	Args:
		curpos (int): current position of the buffer
		initialpos (int): initial position where the parser started working
		tokenend_idx (int): last relevant character index within the last buffered value

	Returns:
		int: length of index
	"""
	return curpos-initialpos+tokenend_idx

def parse_comment(initialpos: int, inp: Iterator[PInput]) -> TokenComment:
	"""Parses input stream into a comment

	Args:
		initialpos (int): initial position where we started
		inp (Iterator[PInput])

	Returns:
		TokenComment
	"""
	curtoken = b""
	for curpos, s in inp:
		m = EOL.search(s, 0)
		if not m:
			curtoken += s
		else:
			j = m.start(0)
			curtoken += s[:j]
			return TokenComment(
				initialpos, 
				cmp_tsize(curpos, initialpos, j), 
				curtoken
			)

def parse_number(initialpos: int, inp: Iterator[PInput]) -> TokenNumber:
	"""Parses input stream into a comment

	Args:
		initialpos (int): initial position where we started
		inp (Iterator[PInput])

	Returns:
		TokenComment
	"""
	curtoken = b""
	is_dec = False
	for curpos, s in inp:
		m = END_NUMBER.search(s, 0)
		if not m:
			curtoken += s
		else:
			j = m.start(0)
			curtoken += s[:j]
			c = s[j : j + 1]
			if (c == b".") and not is_dec:
				is_dec = True
				curtoken += c
				s = s[j+1:]
				m = END_NUMBER.search(s, 0)
				if not m:
					curtoken += s
					continue
				else:
					nj = m.start(0)
					curtoken += s[:nj]
					j += nj
				return TokenDecimal(
					initialpos, 
					cmp_tsize(curpos, initialpos, j), 
					Decimal(curtoken.decode())
				)
			try:
				if is_dec:
					return TokenDecimal(
						initialpos, 
						cmp_tsize(curpos, initialpos, j), 
						Decimal(curtoken.decode())
					)
				else:
					return TokenInteger(
						initialpos, 
						cmp_tsize(curpos, initialpos, j), 
						int(curtoken)
					)
			except ValueError:
				raise InvalidToken(initialpos, curtoken)

# def parse_float(
# 	initialpos: int, 
# 	inp: Iterator[PInput], 
# 	initialtokenval = b""
# ) -> TokenFloat:
# 	curtoken = b"" + initialtokenval
# 	for curpos, s in inp:
# 		print('->',curpos, s)
# 		m = END_NUMBER.search(s, 0)
# 		if not m:
# 			curtoken += s
# 		else:
# 			j = m.start(0)
# 			curtoken += s[:j]
# 			next_t = s[j:j+1]
# 			if next_t == b'.':
# 				curtoken += b'.'
# 				s = s[j+1:]
# 				m = END_NUMBER.search(s, 0)
# 				if not m:
# 					curtoken += s
# 					continue
# 				else:
# 					j = m.start(0)
# 					curtoken += s[:j]
# 					next_t = s[j+1]
# 			try:
# 				print(curpos,j, initialpos)
# 				return TokenFloat(
# 					initialpos, 
# 					cmp_tsize(curpos, initialpos, j), 
# 					Decimal(curtoken.decode())
# 				)
# 			except ValueError:
# 				raise InvalidToken(initialpos, curtoken)
