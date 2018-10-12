import zlib

from ..PSStackParser import PSException
from ..PSStackParser import PSObject
from ...utils import lzwdecode, settings

from .constants import * # pylint: disable=W0614
from .types import * # pylint: disable=W0614
from .exceptions import * # pylint: disable=W0614

##  PDFObjRef
##
class PDFObjRef(PDFObject):

    def __init__(self, doc, objid, _):
        if objid == 0:
            if settings.STRICT:
                raise PDFValueError('PDF object id cannot be 0.')
        self.doc = doc
        self.objid = objid
        #self.genno = genno  # Never used.
        return

    def __repr__(self):
        return '<PDFObjRef:%d>' % (self.objid)

    def resolve(self, default=None):
        try:
            return self.doc.getobj(self.objid)
        except PDFObjectNotFound:
            return default

