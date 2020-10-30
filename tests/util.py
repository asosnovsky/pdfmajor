from pathlib import Path

from pdfmajor.streambuffer import BufferStream

CURRENT_FOLDER = Path(__file__).parent

all_pdf_files = {
    file_path.name: BufferStream(file_path.open("rb"))
    for file_path in (CURRENT_FOLDER / "samples" / "pdf").iterdir()
}
