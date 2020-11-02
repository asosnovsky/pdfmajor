from pdfmajor.streambuffer import BufferStream
from .PDFStream import PDFStream
from .fliters import process_filters_on_data


# class PDFStreamPasrser(PDFParser):
#     def __init__(
#         self,
#         stream: PDFStream,
#         buffer: BufferStream,
#         strict: bool = True,
#     ) -> None:
#         cur_pos = buffer.tell()
#         buffer.seek(stream.offset)
#         data = buffer.read(stream.length).data
#         buffer.seek(cur_pos)
#         data = process_filters_on_data(data, stream.filter, stream.decode_parms)
#         data = process_filters_on_data(data, stream.ffilter, stream.fdecode_parms)
#         self.stream = stream
#         super().__init__(
#             buffer=BufferStream(io.BytesIO(data), buffer_size=stream.length),
#             strict=strict,
#         )
