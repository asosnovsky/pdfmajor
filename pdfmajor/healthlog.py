import traceback
from typing import List, NamedTuple


class PDFHealthLog(NamedTuple):
    """A log of for an issue that the pdf file contains"""

    issue_name: str
    additional_info: str


class PDFHealthReport(List[PDFHealthLog]):
    """a list of all issues that occured during the parsing of the document"""

    def write(self, issue_name: str, additional_info: str):
        self.append(PDFHealthLog(issue_name, additional_info))

    def write_error(self, err: Exception):
        tb = traceback.TracebackException.from_exception(err)
        self.write(err.__class__.__name__, "\n".join(tb.format()))

    def pretty_print(self):
        print("<---HEALTH REPORT--->")
        for issue_name, info in self:
            print(" > ", issue_name)
            print(" |-> ", info)
        if len(self) == 0:
            print(" > No Issues Found.")
        print("</---HEALTH REPORT--->")
