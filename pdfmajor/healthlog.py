from dataclasses import dataclass
from typing import List, NamedTuple


class PDFHealthLog(NamedTuple):
    """A log of for an issue that the pdf file contains"""

    issue_name: str
    additional_info: str


class PDFHealthReport(List[PDFHealthLog]):
    """a list of all issues that occured during the parsing of the document"""

    def write(self, issue_name: str, additional_info: str):
        self.append(PDFHealthLog(issue_name, additional_info))
