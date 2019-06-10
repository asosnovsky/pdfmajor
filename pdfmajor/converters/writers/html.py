from typing import Optional
from io import TextIOWrapper
from contextlib import contextmanager

class HTMLMaker:
    class AccessError(Exception): pass
    def __init__(self, file_path: str, codec: str = 'utf-8'):
        self.file_path = file_path
        self.codec = codec
        self.outfile: Optional[TextIOWrapper] = None
    
    def __enter__(self):
        self.outfile = open(self.file_path, 'wb')
        self.__levels_deep = 0
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.outfile.close()
        self.outfile = None
    
    def write_raw(self, text):
        if self.outfile is not None:
            if self.codec:
                text = text.encode(self.codec)
            self.outfile.write(text)
        else:
            raise self.AccessError("Attempting to write to file without an open connection")
    
    def write(self, text: str, lineend: str = '\n', deep_space: str = ' '):
        text = deep_space*self.__levels_deep + text + lineend
        self.write_raw(text)

    @contextmanager
    def elm(self, tag_name: str, attrs: dict = None, css: dict = None, nolineend: bool = False, no_additional_char: bool = False, singleton: bool = False):
        lineend = '\n'
        deep_space = ' '
        if no_additional_char:
            lineend = ''
            deep_space = ''
        if attrs is None:
            attrs = {}
        if css is not None:
            attrs['style'] = ";".join([
                f'{name}: {value}'
                for name, value in css.items()
            ])
        attrs_str = " ".join([
            f'{name}="{value}"'
            for name, value in attrs.items()
        ])
        if not singleton:
            self.write(f"<{tag_name} {attrs_str}>", lineend=lineend)
            self.__levels_deep += 1
            yield
            self.__levels_deep -= 1
            self.write(f"</{tag_name}>", deep_space=deep_space, lineend='\n' if not nolineend else '')
        else:
            self.write(f"<{tag_name} {attrs_str} />", lineend=lineend, deep_space=deep_space)
            yield
    
    def singleton(self, tag_name: str, attrs: dict = None, css: dict = None, singleton: bool = True):
        with self.elm(tag_name, attrs, css, singleton=singleton):
            pass
