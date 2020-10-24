import io
from typing import Iterator, NamedTuple, Optional
from pdfmajor.exceptions import PDFMajorException


class StreamEOF(PDFMajorException, EOFError):
    def __init__(self) -> None:
        super().__init__("reached the end of the file or buffer stream!")


class BufferedBytes(NamedTuple):
    pos: int
    data: bytes


class BufferStream:
    """A safe reader for bytes that has a few nice additional utilities"""

    __slots__ = ["fp", "buffer_size"]

    def __init__(self, fp: io.BufferedIOBase, buffer_size: int = 4096) -> None:
        """[summary]

        Args:
            fp (io.BufferedIOBase)
            buffer_size (int, optional): maximum length of the bytes this will read at each iteration. Defaults to 4096.
        """
        self.fp = fp
        self.buffer_size = buffer_size

    def get_slice(
        self, offset: int, length: int, buffer_size: Optional[int] = None
    ) -> "BufferStream":
        """Creates a slice of the current byte-stream and returns a BufferStream based on that slice
        Args:
            offset (int): where the slice starts
            length (int): length of the slice
            buffer_size (int, optional) buffer size for new slice. Defaults to self.buffer_size
        Returns:
            BufferStream
        """
        cur_pos = self.tell()
        self.seek(offset)
        bslice = self.fp.read(length)
        self.seek(cur_pos)
        return BufferStream(
            io.BytesIO(bslice),
            buffer_size=buffer_size if buffer_size is not None else self.buffer_size,
        )

    def seekd(self, step: int) -> int:
        """similar to self.fp.seek but you move the offset relative to where you are now

        Args:
            step (int): number of steps to move
        """
        cur_pos = self.tell()
        return self.seek(max(cur_pos + step, 0))

    def seek(self, offset: int) -> int:
        """moves the offset of the reader to a certain spot, and returns the new offset

        Args:
            offset (int)

        Returns:
            int: new offset
        """
        return self.fp.seek(offset)

    def tell(self) -> int:
        """returns the current offset

        Returns:
            int: current offset
        """
        return self.fp.tell()

    def read(self, size: int) -> BufferedBytes:
        """Reads the amount of bytes specified

        Args:
            size (int): number of bytes to read

        Returns:
            BufferedBytes
        """
        pos = self.tell()
        buf = self.fp.read(size)
        return BufferedBytes(pos, buf)

    def readline(self) -> BufferedBytes:
        """Reads upto a line-end

        Returns:
            BufferedBytes
        """
        pos = self.tell()
        buf = self.fp.readline()
        return BufferedBytes(pos, buf)

    def get_firstnonempty_line(self) -> Optional[BufferedBytes]:
        """reads line-by-line until we find a none-empty line

        Returns:
            Optional[BufferedBytes]
        """
        for bbline in self.into_line_iter():
            if bbline.data.strip():
                return bbline
        return None

    def __iter__(self):
        if self.fp.read(1) == b"":
            raise StreamEOF
        self.seekd(-1)
        return self

    def __next__(self):
        bbyte = self.read(self.buffer_size)
        if len(bbyte.data) == 0:
            raise StopIteration(f"no data {bbyte}")
        return bbyte

    def close(self):
        self.fp.close()

    def __del__(self):
        self.close()

    def __exit__(self):
        self.close()

    def into_line_iter(self) -> Iterator[BufferedBytes]:
        """reads the stream line by line

        Raises:
            StreamEOF

        Yields:
            BufferedBytes
        """
        last_pos = self.tell()
        while True:
            bbyte = self.readline()
            if self.tell() == last_pos:
                raise StreamEOF
            yield bbyte
            last_pos = bbyte.pos

    def into_reverse_reader_iter(self) -> Iterator[BufferedBytes]:
        """reads the file in reverse, outputting complete lines

        Yields:
            BufferedBytes
        """
        self.fp.seek(0, 2)
        pos = self.fp.tell()
        buf = b""
        n = -1
        while 0 < pos:
            prevpos = pos
            pos = max(0, pos - self.buffer_size)
            self.fp.seek(pos)
            s = self.fp.read(prevpos - pos)
            if not s:
                break
            while True:
                n = max(s.rfind(b"\r"), s.rfind(b"\n"))
                if n == -1:
                    buf = s + buf
                    break
                yield BufferedBytes(pos=n + 1, data=(s[n + 1 :] + buf))
                s = s[:n]
                buf = b""
        if len(buf) > 0 and pos == 0 and n == -1:
            yield BufferedBytes(pos=n + 1, data=buf)
