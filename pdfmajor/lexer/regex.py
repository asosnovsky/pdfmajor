import re

EOL = re.compile(br"[\r\n]")
END_KEYWORD = re.compile(br"[#/%\[\]()<>{}\s]")
HEX = re.compile(br"[0-9a-fA-F]")
END_LITERAL = re.compile(br"[#/%\[\]()<>{}\s]")
END_STRING = re.compile(br"[()\134]")
OCT_STRING = re.compile(br"^[0-7]{1,3}$")
ESC_STRING = {
    b"b": 8,
    b"t": 9,
    b"n": 10,
    b"f": 12,
    b"r": 13,
    b"(": 40,
    b")": 41,
    b"\\": 92,
}
