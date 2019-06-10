from typing import Set
from json import dumps as json_dump
from io import TextIOWrapper
from contextlib import contextmanager     

@contextmanager
def JSONMaker(file_path: str, codec: str = 'utf-8'):
    with open(file_path, 'wb') as outf:
        with JSONMakerObject(outf, codec=codec) as obj:
            yield obj

class JSONMakerObject:
    class AccessError(Exception): pass
    def __init__(self, outfile: TextIOWrapper, codec: str = 'utf-8', levels_deep: int = 0):
        self.outfile: TextIOWrapper = outfile
        self.codec = codec
        self.levels_deep = levels_deep
        self.keys: Set[str] = set()

    def __enter__(self):
        self.write_raw('{')
        self.levels_deep += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.levels_deep -= 1
        self.write('}', prefix='\n')
    
    def write_raw(self, text):
        if self.outfile is not None:
            if self.codec:
                text = text.encode(self.codec)
            self.outfile.write(text)
        else:
            raise self.AccessError("Attempting to write to file without an open connection")
    
    def write(self, text: str, deep_space: str = '  ', prefix:str = ''):
        text = prefix + (deep_space*self.levels_deep) + text
        self.write_raw(text)

    def write_prop(self, key: str, val: str = ""):
        if key not in self.keys:
            self.keys.add(key)
            if len(self.keys) > 1:
                self.write(f'"{key}": {val}', prefix=',\n')
            else:
                self.write(f'"{key}": {val}', prefix='\n')
 
    def number(self, key: str, val: float or int):
        self.write_prop(key, val)
    
    def string(self, key: str, val: str):
        val_sant = str(val).replace('"', '\\"')
        self.write_prop(key, f'"{val_sant}"')
    
    @contextmanager
    def object(self, key: str):
        self.write_prop(key)
        with JSONMakerObject(self.outfile, codec=self.codec, levels_deep=self.levels_deep) as child:
            yield child
    
    @contextmanager
    def array(self, key: str):
        self.write_prop(key)
        with JSONMakerArray(self.outfile, codec=self.codec, levels_deep=self.levels_deep) as child:
            yield child
    
    def place_object(self, key: str, obj: dict):
        self.write_prop(key, json_dump(obj))
    
    

class JSONMakerArray:
    class AccessError(Exception): pass
    def __init__(self, outfile: TextIOWrapper, codec: str = 'utf-8', levels_deep: int = 0):
        self.outfile: TextIOWrapper = outfile
        self.codec = codec
        self.levels_deep = levels_deep
        self.childrencount = 0

    def __enter__(self):
        self.write_raw('[')
        self.levels_deep += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.levels_deep -= 1
        self.write(']', prefix='\n')
    
    def write_raw(self, text):
        if self.outfile is not None:
            if self.codec:
                text = text.encode(self.codec)
            self.outfile.write(text)
        else:
            raise self.AccessError("Attempting to write to file without an open connection")
    
    def write(self, text: str, deep_space: str = '  ', prefix:str = ''):
        text = prefix + (deep_space*self.levels_deep) + text
        self.write_raw(text)

    def write_prop(self, val: str = ""):
        self.childrencount += 1
        if self.childrencount > 1:
            self.write(f'{val}', prefix=',\n')
        else:
            self.write(f'{val}', prefix='\n')

    def number(self, val: float or int):
        self.write_prop(val)
    
    def string(self, val: str):
        val_sant = str(val).replace('"', '\\"')
        self.write_prop(f'"{val_sant}"')
    
    @contextmanager
    def object(self):
        self.write_prop()
        with JSONMakerObject(self.outfile, codec=self.codec, levels_deep=self.levels_deep) as child:
            yield child
    
    @contextmanager
    def array(self):
        self.write_prop()
        with JSONMakerArray(self.outfile, codec=self.codec, levels_deep=self.levels_deep) as child:
            yield child
    
    def place_object(self, obj: dict):
        self.write_prop(json_dump(obj))
    
    