import logging
from io import TextIOWrapper

from ...utils import choplist, settings

from .PSBaseParser import PSBaseParser
from .types import *
from .exceptions import *
from .constants import *

log = logging.getLogger(__name__)

def literal_name(x):
    if not isinstance(x, PSLiteral):
        if settings.STRICT:
            raise PSTypeError('Literal required: %r' % (x,))
        else:
            name=x
    else:
        name=x.name
        try:
            name = str(name,'utf-8')
        except:
            pass
    return name

def keyword_name(x):
    if not isinstance(x, PSKeyword):
        if settings.STRICT:
            raise PSTypeError('Keyword required: %r' % x)
        else:
            name=x
    else:
        name=x.name
        name = str(name,'utf-8','ignore')
    return name



class PSStackParser(PSBaseParser):

    def __init__(self, fp: TextIOWrapper):
        PSBaseParser.__init__(self, fp)
        self.reset()
        return

    def reset(self):
        self.context = []
        self.curtype = None
        self.curstack = []
        self.results = []
        return

    def seek(self, pos):
        PSBaseParser.seek(self, pos)
        self.reset()
        return

    def push(self, *objs):
        self.curstack.extend(objs)
        return

    def pop(self, n):
        objs = self.curstack[-n:]
        self.curstack[-n:] = []
        return objs

    def popall(self):
        objs = self.curstack
        self.curstack = []
        return objs

    def add_results(self, *objs):
        try:
            log.debug('add_results: %r', objs)
        except:
            log.debug('add_results: (unprintable object)')
        self.results.extend(objs)
        return

    def start_type(self, pos, type):
        self.context.append((pos, self.curtype, self.curstack))
        (self.curtype, self.curstack) = (type, [])
        log.debug('start_type: pos=%r, type=%r', pos, type)
        return

    def end_type(self, type):
        if self.curtype != type:
            raise PSTypeError('Type mismatch: %r != %r' % (self.curtype, type))
        objs = [obj for (_, obj) in self.curstack]
        (pos, self.curtype, self.curstack) = self.context.pop()
        log.debug('end_type: pos=%r, type=%r, objs=%r', pos, type, objs)
        return (pos, objs)

    def do_keyword(self, pos, token):
        return

    def nextobject(self):
        """Yields a list of objects.

        Returns keywords, literals, strings, numbers, arrays and dictionaries.
        Arrays and dictionaries are represented as Python lists and dictionaries.
        """
        while not self.results:
            (pos, token) = self.nexttoken()
            if isinstance(token, (int, float, bool, str, bytes, PSLiteral)):
                # normal token
                self.push((pos, token))
            elif token == KEYWORD_ARRAY_BEGIN:
                # begin array
                self.start_type(pos, 'a')
            elif token == KEYWORD_ARRAY_END:
                # end array
                try:
                    self.push(self.end_type('a'))
                except PSTypeError:
                    if settings.STRICT:
                        raise
            elif token == KEYWORD_DICT_BEGIN:
                # begin dictionary
                self.start_type(pos, 'd')
            elif token == KEYWORD_DICT_END:
                # end dictionary
                try:
                    (pos, objs) = self.end_type('d')
                    if len(objs) % 2 != 0:
                        raise PSSyntaxError('Invalid dictionary construct: %r' % objs)
                    # construct a Python dictionary.
                    d = dict((literal_name(k), v) for (k, v) in choplist(2, objs) if v is not None)
                    self.push((pos, d))
                except PSTypeError:
                    if settings.STRICT:
                        raise
            elif token == KEYWORD_PROC_BEGIN:
                # begin proc
                self.start_type(pos, 'p')
            elif token == KEYWORD_PROC_END:
                # end proc
                try:
                    self.push(self.end_type('p'))
                except PSTypeError:
                    if settings.STRICT:
                        raise
            elif isinstance(token,PSKeyword):
                log.debug('do_keyword: pos=%r, token=%r, stack=%r', pos, token, self.curstack)
                self.do_keyword(pos, token)
            else:
                log.error('unknown token: pos=%r, token=%r, stack=%r', pos, token, self.curstack)
                self.do_keyword(pos, token)
                raise Exception("unknown tokens")
            if self.context:
                continue
            else:
                self.flush()
        obj = self.results.pop(0)
        try:
            log.debug('nextobject: %r', obj)
        except:
            log.debug('nextobject: (unprintable object)')
        return obj
