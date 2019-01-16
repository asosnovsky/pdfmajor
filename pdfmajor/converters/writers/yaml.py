from json import dumps as json_dump
from io import TextIOWrapper
from contextlib import contextmanager     

@contextmanager
def YAMLMaker(file_path: str, codec: str = 'utf-8'):
    with open(file_path, 'wb') as outf:
        with YAMLMakerObject(outf, codec=codec) as obj:
            yield obj

class YAMLMakerWriter:
    class AccessError(Exception): pass
    def __init__(self, outfile: TextIOWrapper, codec: str = 'utf-8', levels_deep: int = -1):
        self.outfile: TextIOWrapper = outfile
        self.codec = codec
        self.levels_deep = levels_deep

    def __enter__(self):
        if self.levels_deep > 0:
            self.__write_raw('')
        self.levels_deep += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.levels_deep -= 1
    
    def __write_raw(self, text):
        if self.outfile is not None:
            if self.codec:
                text = text.encode(self.codec)
            self.outfile.write(text)
        else:
            raise self.AccessError("Attempting to write to file without an open connection")
    
    def _write(self, text: str, append_deep: bool = True, deep_space: str = '  ', prefix:str = ''):
        if not append_deep:
            deep_space = ""
        text = prefix + (deep_space*self.levels_deep) + text
        self.__write_raw(text)

class YAMLMakerObject(YAMLMakerWriter):
    def __init__(self, outfile: TextIOWrapper, codec: str = 'utf-8', levels_deep: int = -1, parent_is_array: bool = False):
        YAMLMakerWriter.__init__(self, outfile, codec, levels_deep)
        self.keys = set()
        self.parent_is_array = parent_is_array

    def write(self, key: str, value: str):
        if key not in self.keys:
            self.keys.add(key)
            if len(self.keys) > 1:
                self._write(f'{key}: {value}', prefix='\n')
            else:
                self._write(f'{key}: {value}', prefix='', 
                    append_deep=not self.parent_is_array
                )
    
    @contextmanager
    def object(self, key: str):
        if key not in self.keys:
            self.keys.add(key)
        if len(self.keys) > 1:
            self._write(f'{key}:\n', prefix='\n')
        else:
            self._write(f'{key}:\n', prefix='', append_deep=False)
        with YAMLMakerObject(self.outfile, codec=self.codec, levels_deep=self.levels_deep) as obj:
            yield obj
    
    @contextmanager
    def array(self, key: str):
        if key not in self.keys:
            self.keys.add(key)
        if len(self.keys) > 1:
            self._write(f'{key}:\n', prefix='\n')
        else:
            self._write(f'{key}:\n', prefix='')
        with YAMLMakerArray(self.outfile, codec=self.codec, levels_deep=self.levels_deep) as obj:
            yield obj
    
    def place_object(self, key: str, obj: dict):
        with self.object(key) as child:
            for key, val in obj.items():
                child.write(key, val)   

    def place_array(self, key: str, arr: list):
        with self.array(key) as child:
            for val in arr:
                child.write(val)


class YAMLMakerArray(YAMLMakerWriter):
    def __init__(self, outfile: TextIOWrapper, codec: str = 'utf-8', levels_deep: int = -1):
        YAMLMakerWriter.__init__(self, outfile, codec, levels_deep)
        self.childrencount = 0 
 
    def write(self, value: str = ""):
        self.childrencount += 1
        if self.childrencount > 1:
            self._write(f'- {value}', prefix='\n')
        else:
            self._write(f'- {value}', prefix='')
    
    @contextmanager
    def object(self):
        self.childrencount += 1
        if self.childrencount > 1:
            self._write(f'- ', prefix='\n')
        else:
            self._write(f'- ', prefix='')
        with YAMLMakerObject(self.outfile, codec=self.codec, levels_deep=self.levels_deep, parent_is_array=True) as obj:
            yield obj
    
    def place_object(self, obj: dict):
        with self.object() as child:
            for key, val in obj.items():
                child.write(key, val)   

    