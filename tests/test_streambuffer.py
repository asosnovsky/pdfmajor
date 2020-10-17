import io
from unittest import TestCase
from pdfmajor.streambuffer import StreamEOF, BufferStream


class UseCase(TestCase):
    def test_safebuff(self):
        for bufsize in [2, 33, 65, 66, 100, 200]:
            it = BufferStream(
                io.BytesIO(
                    b"this is a lengthy comment that ends here\nso this is not reachable"
                ),
                buffer_size=bufsize,
            )
            for subbuf in it:
                self.assertLessEqual(len(subbuf), it.buffer_size)

    def test_itraises(self):
        it = BufferStream(io.BytesIO(b"this"))
        list(it)  # read everything
        with self.assertRaises(StreamEOF):
            for _ in it:
                pass
        with self.assertRaises(EOFError):
            for _ in it:
                pass

    def test_seekd(self):
        for bufsize in [2, 33, 65, 66, 100, 200]:
            it = BufferStream(
                io.BytesIO(
                    b"this is a lengthy comment that ends here\nso this is not reachable"
                ),
                buffer_size=bufsize,
            )
            last_buf = next(it)
            it.seekd(-it.buffer_size)
            for i, buf in enumerate(it):
                self.assertEqual(last_buf, buf)
                it.seekd(-it.buffer_size)
                if i > 4:
                    break
