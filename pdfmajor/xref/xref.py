from typing import Iterator, Literal, NamedTuple, Union

from pdfmajor.lexer import iter_tokens
from pdfmajor.lexer.token import TokenInteger, TokenKeyword
from pdfmajor.streambuffer import BufferStream

from .exceptions import BrokenFile, PDFNoValidXRef, UnexpectedEOF


class XRefRow(NamedTuple):
    """a parsed version of a row in the xref table
    as defined in PDF spec 1.7 section 7.5.4
    """

    offset: int
    obj_num: int
    gen_num: int
    use: Union[Literal["n"], Literal["f"]]


def find_start_of_xref(buffer: BufferStream, strict: bool = False) -> int:
    """Internal function used to locate the start of the XRef table"""
    prev = None
    found_eof = False
    for _, line in buffer.into_reverse_reader_iter():
        line = line.strip()
        found_eof |= line.strip() == b"%%EOF"
        if line == b"startxref":
            break
        if line:
            prev = line
    if prev is None:
        raise PDFNoValidXRef()
    if strict and not found_eof:
        raise BrokenFile(
            "Failed to find %%EOF at end of file, this can indicate the file is incomplete or broken."
        )
    return int(prev)


def iter_over_xref(
    buffer: BufferStream, start_offset: int, strict: bool = False
) -> Iterator[XRefRow]:
    buffer.seek(start_offset)
    first_token = next(iter_tokens(buffer))
    if isinstance(first_token, TokenInteger):
        raise NotImplementedError("XRefStream: PDF-1.5")
    elif isinstance(first_token, TokenKeyword):
        if first_token.value == b"xref":
            yield from iter_over_standard_xref(buffer, strict)
    else:
        raise BrokenFile("Missing a valid XRef table")


#     # read xref table
#     def read_xref_from(self, parser, start, xrefs):
#         """Reads XRefs from the given location."""
#         parser.seek(start)
#         parser.reset()
#         try:
#             (pos, token) = parser.nexttoken()
#         except PSEOF:
#             raise PDFNoValidXRef("Unexpected EOF")
#         log.info("read_xref_from: start=%d, token=%r", start, token)
#         if isinstance(token, int):
#             # XRefStream: PDF-1.5
#             parser.seek(pos)
#             parser.reset()
#             xref = PDFXRefStream()
#             xref.load(parser)
#         else:
#             if token is parser.KEYWORD_XREF:
#                 parser.nextline()
#             xref = PDFXRef()
#             xref.load(parser)
#         xrefs.append(xref)
#         trailer = xref.get_trailer()
#         log.info("trailer: %r", trailer)
#         if "XRefStm" in trailer:
#             pos = int_value(trailer["XRefStm"])
#             self.read_xref_from(parser, pos, xrefs)
#         if "Prev" in trailer:
#             # find previous xref
#             pos = int_value(trailer["Prev"])
#             self.read_xref_from(parser, pos, xrefs)
#         return


def iter_over_standard_xref(
    buffer: BufferStream, strict: bool = False
) -> Iterator[XRefRow]:
    while True:
        bbline = buffer.get_firstnonempty_line()
        if bbline is None:
            raise UnexpectedEOF
        pos, line = bbline
        if line.startswith(b"trailer"):
            buffer.seek(pos)
            break
        descriptors = line.strip().split(b" ")
        if len(descriptors) != 2:
            raise PDFNoValidXRef(f"Trailer not found: pos={pos} line={line!r}")
        try:
            (start, nobjs) = map(int, descriptors)
        except ValueError:
            raise PDFNoValidXRef(
                f"Failed to decipher xref row: pos={pos} line={line!r}"
            )
        for obj_num in range(start, start + nobjs):
            _, line = buffer.readline()
            f = line.strip().split(b" ")
            if len(f) != 3:
                raise PDFNoValidXRef(f"Invalid XRef format: pos={pos} line={line!r}")
            try:
                pos = int(f[0])
                gen_num = int(f[1])
                use = f[2]
            except ValueError:
                raise PDFNoValidXRef(
                    f"Failed to decipher xref row: pos={pos} line={line!r}"
                )
            if use not in [b"n", b"f"] and not strict:
                raise PDFNoValidXRef(
                    f"Invalid 'use' value for xref {use!r}: pos={pos} line={line!r}"
                )
            yield XRefRow(offset=pos, obj_num=obj_num, gen_num=gen_num, use=use)  # type: ignore


# def construct_indobj_collection(
#     buffer: BufferStream, it_xref: Iterator[XRefRow]
# ) -> IndirectObjectCollection:
#     collection = IndirectObjectCollection()
# parser =
