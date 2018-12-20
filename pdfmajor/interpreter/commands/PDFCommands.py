from typing import List

from pdfmajor.utils import MATRIX_IDENTITY, mult_matrix
from pdfmajor.parser.PSStackParser import literal_name
from pdfmajor.parser.PDFStream import PDFStream, list_value, dict_value
from pdfmajor.parser.constants import LITERAL_FORM, LITERAL_IMAGE
from .state import PDFStateStack, PDFColorSpace
from .state.Curves import CurveMethod, CurvePath, CurvePoint

class PDFCommands:
    commands = {}
    class InvalidOperation(Exception): pass
    class RepeatedCommand(Exception): pass

    @classmethod
    def __add(cls, cmd_name: str, cmd: callable):
        if not (cmd_name in cls.commands.keys()):
            cls.commands[cmd_name] = cmd
            return cmd
        raise cls.RepeatedCommand(cmd_name)

    @classmethod
    def add(cls, *cmd_names: List[str]):
        def wrap(cmd: callable):
            for cmd_name in cmd_names:
                cls.__add(cmd_name, cmd)
            return cmd
        return wrap


