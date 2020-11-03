import traceback
import warnings
from typing import List


class PDFMajorWarning(Warning):
    def __init__(self, issue_name: str, additional_info: str) -> None:
        self.issue_name = issue_name
        self.additional_info = additional_info
        super().__init__(f"health issue detected: {issue_name}: {additional_info}")


class PDFHealthReport(List[PDFMajorWarning]):
    """a list of all issues that occured during the parsing of the document"""

    def write(self, issue_name: str, additional_info: str):
        log = PDFMajorWarning(issue_name, additional_info)
        warnings.warn(log)
        self.append(log)

    def write_error(self, err: Exception):
        tb = traceback.TracebackException.from_exception(err)
        self.write(err.__class__.__name__, "\n".join(tb.format()))

    def __repr__(self) -> str:
        out = "<---HEALTH REPORT--->"
        for log in self:
            out += "\n"
            out += f" > {log.issue_name}"
            out += f" |-> {log.additional_info}"
        out += "</---HEALTH REPORT--->"
        return out
