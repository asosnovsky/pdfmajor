import re

EOL = re.compile(br"[\r\n]")
END_KEYWORD = re.compile(br"[#/%\[\]()<>{}\s]")
HEX = re.compile(br"[0-9a-fA-F]")
END_LITERAL = re.compile(br"[#/%\[\]()<>{}\s]")
