import io
from unittest import TestCase

from pdfmajor.streambuffer import BufferStream, StreamEOF


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
        for bufsize in [2, 33, 65, 66, 100, 200]:
            it = BufferStream(io.BytesIO(b"this"), buffer_size=bufsize)
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

    def test_reverse_reader(self):
        for bufsize in [2, 33, 65, 66, 100, 200, 600, 1000]:
            it = BufferStream(
                io.BytesIO(
                    b"""xref
0 32
0000000000 65535 f 
0000027259 00000 n 
0000000019 00000 n 
0000000344 00000 n 
0000027402 00000 n 
0000000364 00000 n 
0000000714 00000 n 
0000027545 00000 n 
0000000734 00000 n 
0000005949 00000 n 
0000005970 00000 n 
0000006176 00000 n 
0000006503 00000 n 
0000006700 00000 n 
0000011679 00000 n 
0000011701 00000 n 
0000011905 00000 n 
0000012232 00000 n 
0000012427 00000 n 
0000017804 00000 n 
0000017826 00000 n 
0000018037 00000 n 
0000018364 00000 n 
0000018565 00000 n 
0000026258 00000 n 
0000026280 00000 n 
0000026477 00000 n 
0000026882 00000 n 
0000027141 00000 n 
0000027204 00000 n 
0000027650 00000 n 
0000027747 00000 n 
trailer
<</Size 32/Root 30 0 R
/Info 31 0 R
/ID [ <4FCA78642D7C01696E050B630CE27BE4>
<4FCA78642D7C01696E050B630CE27BE4> ]
/DocChecksum /6647D1C1022900091A1C5A662E91248C
>>
startxref
27922
%%EOF"""
                ),
                buffer_size=bufsize,
            )
            expected = [
                b"%%EOF",
                b"27922",
                b"startxref",
                b">>",
                b"/DocChecksum /6647D1C1022900091A1C5A662E91248C",
                b"<4FCA78642D7C01696E050B630CE27BE4> ]",
                b"/ID [ <4FCA78642D7C01696E050B630CE27BE4>",
                b"/Info 31 0 R",
                b"<</Size 32/Root 30 0 R",
                b"trailer",
                b"0000027747 00000 n ",
                b"0000027650 00000 n ",
                b"0000027204 00000 n ",
                b"0000027141 00000 n ",
                b"0000026882 00000 n ",
                b"0000026477 00000 n ",
                b"0000026280 00000 n ",
                b"0000026258 00000 n ",
                b"0000018565 00000 n ",
                b"0000018364 00000 n ",
                b"0000018037 00000 n ",
                b"0000017826 00000 n ",
                b"0000017804 00000 n ",
                b"0000012427 00000 n ",
                b"0000012232 00000 n ",
                b"0000011905 00000 n ",
                b"0000011701 00000 n ",
                b"0000011679 00000 n ",
                b"0000006700 00000 n ",
                b"0000006503 00000 n ",
                b"0000006176 00000 n ",
                b"0000005970 00000 n ",
                b"0000005949 00000 n ",
                b"0000000734 00000 n ",
                b"0000027545 00000 n ",
                b"0000000714 00000 n ",
                b"0000000364 00000 n ",
                b"0000027402 00000 n ",
                b"0000000344 00000 n ",
                b"0000000019 00000 n ",
                b"0000027259 00000 n ",
                b"0000000000 65535 f ",
                b"0 32",
                b"xref",
            ]
            for (pos, buf), ebuf in zip(it.into_reverse_reader_iter(), expected):
                self.assertEqual(buf, ebuf)
