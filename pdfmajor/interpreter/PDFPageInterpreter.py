import logging
import operator

from typing import List


from .PDFColorSpace import PDFColorSpace
from .PDFColorSpace import PREDEFINED_COLORSPACE

from .cmapdb import CMapDB
from .cmapdb import CMap

from .PDFStream import PDFException
from .PDFStream.PDFObjRef import PDFObjRef
from .PDFStream import resolve1, list_value, dict_value
from .PDFStream import PDFStream

from .PSStackParser import PSEOF
from .PSStackParser import PSKeyword
from .PSStackParser import literal_name
from .PSStackParser import keyword_name
from .PSStackParser import PSStackParser
from .PSStackParser import LIT

from .PDFGraphicState import PDFGraphicState
from .PDFTextState import PDFTextState
from .PDFContentParser import PDFContentParser

from ..utils import settings, mult_matrix, MATRIX_IDENTITY
from .constants import LITERAL_FORM, LITERAL_IMAGE
from .types import CurvePoint, CurvePath

log = logging.getLogger(__name__)

##  Exceptions
##
class PDFInterpreterError(PDFException):
    pass

class PDFPageInterpreter(object):

    def __init__(self, rsrcmgr, device):
        self.rsrcmgr = rsrcmgr
        self.device = device
        self.curpath: List[CurvePath] = []
        return

    def dup(self):
        return self.__class__(self.rsrcmgr, self.device)

    # init_resources(resources):
    #   Prepare the fonts and XObjects listed in the Resource attribute.
    def init_resources(self, resources):
        self.resources = resources
        self.fontmap = {}
        self.xobjmap = {}
        self.csmap = PREDEFINED_COLORSPACE.copy()
        if not resources:
            return

        def get_colorspace(spec):
            if isinstance(spec, list):
                name = literal_name(spec[0])
            else:
                name = literal_name(spec)
            if name == 'ICCBased' and isinstance(spec, list) and 2 <= len(spec):
                return PDFColorSpace(name, PDFStream.validated_stream(spec[1])['N'])
            elif name == 'DeviceN' and isinstance(spec, list) and 2 <= len(spec):
                return PDFColorSpace(name, len(list_value(spec[1])))
            else:
                return PREDEFINED_COLORSPACE.get(name)

        for (k, v) in iter(dict_value(resources).items()):
            log.debug('Resource: %r: %r', k, v)
            if k == 'Font':
                for (fontid, spec) in iter(dict_value(v).items()):
                    objid = None
                    if isinstance(spec, PDFObjRef):
                        objid = spec.objid
                    spec = dict_value(spec)
                    self.fontmap[fontid] = self.rsrcmgr.get_font(objid, spec)
            elif k == 'ColorSpace':
                for (csid, spec) in iter(dict_value(v).items()):
                    self.csmap[csid] = get_colorspace(resolve1(spec))
            elif k == 'ProcSet':
                self.rsrcmgr.get_procset(list_value(v))
            elif k == 'XObject':
                for (xobjid, xobjstrm) in iter(dict_value(v).items()):
                    self.xobjmap[xobjid] = xobjstrm
        return

    # init_state(ctm)
    #   Initialize the text and graphic states for rendering a page.
    def init_state(self, ctm):
        # gstack: stack for graphical states.
        self.gstack = []
        self.ctm = ctm
        self.device.set_ctm(self.ctm)
        self.textstate = PDFTextState()
        self.graphicstate = PDFGraphicState()
        self.curpath = []
        # argstack: stack for command arguments.
        self.argstack = []
        # set some global states.
        self.scs = self.ncs = None
        if self.csmap:
            self.scs = self.ncs = next(iter(self.csmap.values()))
        return

    def push(self, obj):
        self.argstack.append(obj)
        return

    def pop(self, n):
        if n == 0:
            return []
        x = self.argstack[-n:]
        self.argstack = self.argstack[:-n]
        return x

    def get_current_state(self):
        return (self.ctm, self.textstate.copy(), self.graphicstate.copy())

    def set_current_state(self, state):
        (self.ctm, self.textstate, self.graphicstate) = state
        self.device.set_ctm(self.ctm)
        return

    # gsave
    def do_q(self):
        self.gstack.append(self.get_current_state())
        return

    # grestore
    def do_Q(self):
        if self.gstack:
            self.set_current_state(self.gstack.pop())
        return

    # concat-matrix
    def do_cm(self, a1, b1, c1, d1, e1, f1):
        self.ctm = mult_matrix((a1, b1, c1, d1, e1, f1), self.ctm)
        self.device.set_ctm(self.ctm)
        return

    # setlinewidth
    def do_w(self, linewidth):
        self.graphicstate.linewidth = linewidth
        return

    # setlinecap
    def do_J(self, linecap):
        self.graphicstate.linecap = linecap
        return

    # setlinejoin
    def do_j(self, linejoin):
        self.graphicstate.linejoin = linejoin
        return

    # setmiterlimit
    def do_M(self, miterlimit):
        self.graphicstate.miterlimit = miterlimit
        return

    # setdash
    def do_d(self, dash, phase):
        self.graphicstate.dash = (dash, phase)
        return

    # setintent
    def do_ri(self, intent):
        self.graphicstate.intent = intent
        return

    # setflatness
    def do_i(self, flatness):
        self.graphicstate.flatness = flatness
        return

    # load-gstate
    def do_gs(self, name):
        #XXX
        return

    # moveto
    def do_m(self, x: float, y: float):
        self.curpath.append(CurvePath(CurvePath.METHOD.MOVE_TO, CurvePoint(x, y)))
        return

    # lineto
    def do_l(self, x: float, y: float):
        self.curpath.append(CurvePath(CurvePath.METHOD.LINE_TO, CurvePoint(x, y)))
        return

    # curveto
    def do_c(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        self.curpath.append(CurvePath(
            CurvePath.METHOD.CURVE_BOTH_TO, 
            CurvePoint(x1, y1), 
            CurvePoint(x2, y2), 
            CurvePoint(x3, y3),
        ))
        return

    # urveto
    def do_v(self, x2: float, y2: float, x3: float, y3: float):
        self.curpath.append(CurvePath(
            CurvePath.METHOD.CURVE_NEXT_TO, 
            CurvePoint(x2, y2), 
            CurvePoint(x3, y3),
        ))
        return

    # rveto
    def do_y(self, x1: float, y1: float, x3: float, y3: float):
        self.curpath.append(CurvePath(
            CurvePath.METHOD.CURVE_FIRST_TO, 
            CurvePoint(x1, y1), 
            CurvePoint(x3, y3)
        ))
        return

    # closepath
    def do_h(self):
        self.curpath.append(CurvePath(CurvePath.METHOD.CLOSE_PATH))
        return

    # rectangle
    def do_re(self, x, y, w, h):
        self.curpath.append(CurvePath(CurvePath.METHOD.MOVE_TO, CurvePoint(x, y) ))
        self.curpath.append(CurvePath(CurvePath.METHOD.LINE_TO, CurvePoint(x+w, y) ))
        self.curpath.append(CurvePath(CurvePath.METHOD.LINE_TO, CurvePoint(x+w, y+h) ))
        self.curpath.append(CurvePath(CurvePath.METHOD.LINE_TO, CurvePoint(x, y+h) ))
        self.curpath.append(CurvePath(CurvePath.METHOD.CLOSE_PATH))
        return

    # stroke
    def do_S(self):
        self.device.paint_path(self.graphicstate.copy(), False, self.curpath)
        self.curpath = []
        return

    # close-and-stroke
    def do_s(self):
        self.do_h()
        self.do_S()
        return

    # fill
    def do_f(self):
        self.device.paint_path(self.graphicstate.copy(), False, self.curpath)
        self.curpath = []
        return
    # fill (obsolete)
    do_F = do_f

    # fill-even-odd
    def do_f_a(self):
        self.device.paint_path(self.graphicstate.copy(), True, self.curpath)
        self.curpath = []
        return

    # fill-and-stroke
    def do_B(self):
        self.device.paint_path(self.graphicstate.copy(), False, self.curpath)
        self.curpath = []
        return

    # fill-and-stroke-even-odd
    def do_B_a(self):
        self.device.paint_path(self.graphicstate.copy(), True, self.curpath)
        self.curpath = []
        return

    # close-fill-and-stroke
    def do_b(self):
        self.do_h()
        self.do_B()
        return

    # close-fill-and-stroke-even-odd
    def do_b_a(self):
        self.do_h()
        self.do_B_a()
        return

    # close-only
    def do_n(self):
        self.curpath = []
        return

    # clip
    def do_W(self):
        return

    # clip-even-odd
    def do_W_a(self):
        return

    # setcolorspace-stroking
    def do_CS(self, name):
        try:
            self.scs = self.csmap[literal_name(name)]
        except KeyError:
            if settings.STRICT:
                raise PDFInterpreterError('Undefined ColorSpace: %r' % name)
        return

    # setcolorspace-non-strokine
    def do_cs(self, name):
        try:
            self.ncs = self.csmap[literal_name(name)]
        except KeyError:
            if settings.STRICT:
                raise PDFInterpreterError('Undefined ColorSpace: %r' % name)
        return

    # setgray-stroking
    def do_G(self, gray):
        self.graphicstate.scolor.gray = gray
        #self.do_CS(LITERAL_DEVICE_GRAY)
        return

    # setgray-non-stroking
    def do_g(self, gray):
        self.graphicstate.ncolor.gray = gray
        #self.do_cs(LITERAL_DEVICE_GRAY)
        return

    # setrgb-stroking
    def do_RG(self, r, g, b):
        self.graphicstate.scolor.rgb = (r*255, g*255, b*255)
        #self.do_CS(LITERAL_DEVICE_RGB)
        return

    # setrgb-non-stroking
    def do_rg(self, r, g, b):
        self.graphicstate.ncolor.rgb = (r*255, g*255, b*255)
        #self.do_cs(LITERAL_DEVICE_RGB)
        return

    # setcmyk-stroking
    def do_K(self, c, m, y, k):
        self.graphicstate.scolor.cmyk = (c, m, y, k)
        #self.do_CS(LITERAL_DEVICE_CMYK)
        return

    # setcmyk-non-stroking
    def do_k(self, c, m, y, k):
        self.graphicstate.ncolor.cmyk = (c, m, y, k)
        #self.do_cs(LITERAL_DEVICE_CMYK)
        return

    # setcolor
    def do_SCN(self):
        if self.scs:
            n = self.scs.ncomponents
        else:
            if settings.STRICT:
                raise PDFInterpreterError('No colorspace specified!')
            n = 1
        self.pop(n)
        return

    def do_scn(self):
        if self.ncs:
            n = self.ncs.ncomponents
        else:
            if settings.STRICT:
                raise PDFInterpreterError('No colorspace specified!')
            n = 1
        self.pop(n)
        return

    def do_SC(self):
        self.do_SCN()
        return

    def do_sc(self):
        self.do_scn()
        return

    # sharing-name
    def do_sh(self, name):
        return

    # begin-text
    def do_BT(self):
        self.textstate.reset()
        return

    # end-text
    def do_ET(self):
        return

    # begin-compat
    def do_BX(self):
        return

    # end-compat
    def do_EX(self):
        return

    # marked content operators
    def do_MP(self, tag):
        self.device.do_tag(tag)
        return

    def do_DP(self, tag, props):
        self.device.do_tag(tag, props)
        return

    def do_BMC(self, tag):
        self.device.begin_tag(tag)
        return

    def do_BDC(self, tag, props):
        self.device.begin_tag(tag, props)
        return

    def do_EMC(self):
        self.device.end_tag()
        return

    # setcharspace
    def do_Tc(self, space):
        self.textstate.charspace = space
        return

    # setwordspace
    def do_Tw(self, space):
        self.textstate.wordspace = space
        return

    # textscale
    def do_Tz(self, scale):
        self.textstate.scaling = scale
        return

    # setleading
    def do_TL(self, leading):
        self.textstate.leading = -leading
        return

    # selectfont
    def do_Tf(self, fontid, fontsize):
        try:
            self.textstate.font = self.fontmap[literal_name(fontid)]
        except KeyError:
            if settings.STRICT:
                raise PDFInterpreterError('Undefined Font id: %r' % fontid)
            self.textstate.font = self.rsrcmgr.get_font(None, {})
        self.textstate.fontsize = fontsize
        return

    # setrendering
    def do_Tr(self, render):
        self.textstate.render = render
        return

    # settextrise
    def do_Ts(self, rise):
        self.textstate.rise = rise
        return

    # text-move
    def do_Td(self, tx, ty):
        (a, b, c, d, e, f) = self.textstate.matrix
        self.textstate.matrix = (a, b, c, d, tx*a+ty*c+e, tx*b+ty*d+f)
        self.textstate.linematrix = (0, 0)
        return

    # text-move
    def do_TD(self, tx, ty):
        (a, b, c, d, e, f) = self.textstate.matrix
        self.textstate.matrix = (a, b, c, d, tx*a+ty*c+e, tx*b+ty*d+f)
        self.textstate.leading = ty
        self.textstate.linematrix = (0, 0)
        return

    # textmatrix
    def do_Tm(self, a, b, c, d, e, f):
        self.textstate.matrix = (a, b, c, d, e, f)
        self.textstate.linematrix = (0, 0)
        return

    # nextline
    def do_T_a(self):
        (a, b, c, d, e, f) = self.textstate.matrix
        self.textstate.matrix = (a, b, c, d, self.textstate.leading*c+e, self.textstate.leading*d+f)
        self.textstate.linematrix = (0, 0)
        return

    # show-pos
    def do_TJ(self, seq):
        if self.textstate.font is None:
            if settings.STRICT:
                raise PDFInterpreterError('No font specified!')
            return
        self.device.render_string(self.textstate, seq, self.ncs, self.graphicstate.copy())
        return

    # show
    def do_Tj(self, s):
        self.do_TJ([s])
        return

    # quote
    def do__q(self, s):
        self.do_T_a()
        self.do_TJ([s])
        return

    # doublequote
    def do__w(self, aw, ac, s):
        self.do_Tw(aw)
        self.do_Tc(ac)
        self.do_TJ([s])
        return

    # inline image
    def do_BI(self):  # never called
        return

    def do_ID(self):  # never called
        return

    def do_EI(self, obj: PDFStream):
        if 'W' in obj and 'H' in obj:
            iobjid = str(id(obj))
            self.device.begin_figure(iobjid, (0, 0, 1, 1), MATRIX_IDENTITY)
            self.device.render_image(iobjid, obj)
            self.device.end_figure(iobjid)
        return

    # invoke an XObject
    def do_Do(self, xobjid):
        xobjid = literal_name(xobjid)
        try:
            xobj = PDFStream.validated_stream(self.xobjmap[xobjid])
        except KeyError:
            if settings.STRICT:
                raise PDFInterpreterError('Undefined xobject id: %r' % xobjid)
            return
        log.info('Processing xobj: %r', xobj)
        subtype = xobj.get('Subtype')
        if subtype is LITERAL_FORM and 'BBox' in xobj:
            interpreter = self.dup()
            bbox = list_value(xobj['BBox'])
            matrix = list_value(xobj.get('Matrix', MATRIX_IDENTITY))
            # According to PDF reference 1.7 section 4.9.1, XObjects in
            # earlier PDFs (prior to v1.2) use the page's Resources entry
            # instead of having their own Resources entry.
            xobjres = xobj.get('Resources')
            resources = dict_value(xobjres) if xobjres else self.resources.copy()
            self.device.begin_figure(xobjid, bbox, matrix)
            interpreter.render_contents(resources, [xobj], ctm=mult_matrix(matrix, self.ctm))
            self.device.end_figure(xobjid)
        elif subtype is LITERAL_IMAGE and 'Width' in xobj and 'Height' in xobj:
            self.device.begin_figure(xobjid, (0, 0, 1, 1), MATRIX_IDENTITY)
            self.device.render_image(xobjid, xobj)
            self.device.end_figure(xobjid)
        else:
            # unsupported xobject type.
            pass
        return

    def process_page(self, page):
        log.info('Processing page: %r', page)
        (x0, y0, x1, y1) = page.mediabox
        if page.rotate == 90:
            ctm = (0, -1, 1, 0, -y0, x1)
        elif page.rotate == 180:
            ctm = (-1, 0, 0, -1, x1, y1)
        elif page.rotate == 270:
            ctm = (0, 1, -1, 0, y1, -x0)
        else:
            ctm = (1, 0, 0, 1, -x0, -y0)
        self.device.begin_page(page, ctm)
        self.render_contents(page.resources, page.contents, ctm=ctm)
        self.device.end_page(page)
        return

    # render_contents(resources, streams, ctm)
    #   Render the content streams.
    #   This method may be called recursively.
    def render_contents(self, resources, streams, ctm=MATRIX_IDENTITY):
        log.info('render_contents: resources=%r, streams=%r, ctm=%r',
                 resources, streams, ctm)
        self.init_resources(resources)
        self.init_state(ctm)
        self.execute(list_value(streams))
        return

    def execute(self, streams):
        try:
            parser = PDFContentParser(streams)
        except PSEOF:
            # empty page
            return
        while True:
            try:
                (_, obj) = parser.nextobject()
            except PSEOF:
                break
            if isinstance(obj, PSKeyword):
                name = keyword_name(obj)
                method = 'do_%s' % name.replace('*', '_a').replace('"', '_w').replace("'", '_q')
                if hasattr(self, method):
                    func = getattr(self, method)
                    nargs = func.__code__.co_argcount-1
                    if nargs:
                        args = self.pop(nargs)
                        if len(args) == nargs:
                            func(*args)
                    else:
                        log.debug('exec: %s', name)
                        func()
                else:
                    if settings.STRICT:
                        raise PDFInterpreterError('Unknown operator: %r' % name)
            else:
                self.push(obj)
        return
