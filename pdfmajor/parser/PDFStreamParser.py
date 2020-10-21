import io

from .objects.stream import PDFStream
from .state import ParsingState
from .PDFParser import PDFParser
from .fliters import process_filters_on_data


class PDFStreamPasrser(PDFParser):
    def __init__(
        self,
        stream: PDFStream,
        fp: io.BufferedIOBase,
        state: ParsingState,
        buffer_size: int = 4096,
        strict: bool = True,
    ) -> None:
        fp.seek(stream.offset)
        data = fp.read(stream.length)
        data = process_filters_on_data(data, stream.filter, stream.decode_parms)
        data = process_filters_on_data(data, stream.ffilter, stream.fdecode_parms)
        self.stream = stream
        super().__init__(
            fp=io.BytesIO(data),
            buffer_size=buffer_size,
            state=state,
            strict=strict,
            retain_obj_on_seek=True,
        )
