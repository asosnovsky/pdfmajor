from pdfmajor.utils import mult_matrix, MATRIX_IDENTITY, apply_matrix_pt, get_logger
from pdfmajor.parser.PSStackParser import literal_name
from pdfmajor.parser.PDFStream import PDFStream, list_value, dict_value
from pdfmajor.parser.constants import LITERAL_FORM, LITERAL_IMAGE

from .PDFCommands import PDFCommands
from .state import PDFStateStack, PDFGraphicState, LTTextBlock
from .state.Curves import CurveMethod, CurvePath, CurvePoint
# from .state.PDFItem import PDFImage, PDFShape, PDFText, PDFXObject
from .state import make_char_block, make_curve, make_image, make_xobject

log = get_logger('commands')

# No Support
# @PDFCommands.add('W','W_a', 'sh', 'ET', 'BX', 'EX' ,'BI', 'ID', 'gs')
# def do_no_support(stack: PDFStateStack) -> PDFStateStack:
#     # log.debug("Unsupported command")
#     return stack

# marked content operators
# @PDFCommands.add('MP')
# def do_MP(stack: PDFStateStack, tag) -> PDFStateStack:
#     log.debug(f"Unsupported command - do_tag {[tag]}")
#     # self.device.do_tag(tag)
#     return stack

# @PDFCommands.add('DP')
# def do_DP(stack: PDFStateStack, tag, props=None) -> PDFStateStack:
#     log.debug(f"Unsupported command - do_tag {[tag.name, type(tag), props]}")
#     # self.device.do_tag(tag)
#     return stack

# @PDFCommands.add('BMC')
# def do_BMC(stack: PDFStateStack, tag) -> PDFStateStack:
#     log.debug(f"Unsupported command - begin_tag {[tag.name, type(tag)]}")
#     # self.device.begin_tag(tag)
#     return stack

# @PDFCommands.add('BDC')
# def do_BDC(stack: PDFStateStack, tag, props=None) -> PDFStateStack:
#     log.debug(f"Unsupported command - begin_tag {[tag.name, type(tag), props]}")
#     # self.device.begin_tag(tag)
#     return stack

# @PDFCommands.add('EMC')
# def do_EMC(stack: PDFStateStack) -> PDFStateStack:
#     # self.device.end_tag(tag)
#     log.debug("Unsupported command - end_tag")
#     return stack

@PDFCommands.add('q')
def save_state(stack: PDFStateStack) -> PDFStateStack:
    stack.gstack.append([
        stack.t_matrix,
        stack.text.copy(),
        stack.graphics.copy()
    ])
    return stack

@PDFCommands.add('Q')
def restore_state(stack: PDFStateStack) -> PDFStateStack:
    if len(stack.gstack) > 0:
        stack.t_matrix, stack.text, stack.graphicstate = stack.gstack.pop()
    return stack

# concat-matrix
@PDFCommands.add('cm')
def concat_transition_matrix(stack: PDFStateStack, a1, b1, c1, d1, e1, f1) -> PDFStateStack:
    stack.t_matrix = mult_matrix((a1, b1, c1, d1, e1, f1), stack.t_matrix)
    return stack

# setlinewidth
@PDFCommands.add('w')
def set_line_width(stack: PDFStateStack, linewidth) -> PDFStateStack:
    stack.graphics.linewidth = linewidth
    return stack

# setlinecap
@PDFCommands.add('J')
def set_linecap(stack: PDFStateStack, linecap) -> PDFStateStack:
    stack.graphics.linecap = linecap
    return stack

# setlinejoin
@PDFCommands.add('j')
def set_linejoin(stack: PDFStateStack, linejoin) -> PDFStateStack:
    stack.graphics.linejoin = linejoin
    return stack

# setmiterlimit
@PDFCommands.add('M')
def set_miterlimit(stack: PDFStateStack, miterlimit) -> PDFStateStack:
    stack.graphics.miterlimit = miterlimit
    return stack

# setdash
@PDFCommands.add('d')
def set_dash(stack: PDFStateStack, dash, phase) -> PDFStateStack:
    stack.graphics.dash = (dash, phase)
    return stack

# setintent
@PDFCommands.add('ri')
def set_intent(stack: PDFStateStack, intent) -> PDFStateStack:
    stack.graphics.intent = intent
    return stack

# setflatness
@PDFCommands.add('i')
def set_flatness(stack: PDFStateStack, flatness) -> PDFStateStack:
    stack.graphics.flatness = flatness
    return stack

# moveto
@PDFCommands.add('m')
def curve_moveto(stack: PDFStateStack, x: float, y: float) -> PDFStateStack:
    stack.curvestacks.append(CurvePath(
        CurvePath.METHOD.MOVE_TO, 
        CurvePoint(stack.t_matrix, x, y)
    ))
    return stack

# lineto
@PDFCommands.add('l')
def curve_lineto(stack: PDFStateStack, x: float, y: float) -> PDFStateStack:
    stack.curvestacks.append(CurvePath(
        CurvePath.METHOD.LINE_TO, 
        CurvePoint(stack.t_matrix, x, y)
    ))
    return stack

# curveto
@PDFCommands.add('c')
def curve_curveto(stack: PDFStateStack, 
        x1: float, y1: float, 
        x2: float, y2: float, 
        x3: float, y3: float ) -> PDFStateStack:
    stack.curvestacks.append(CurvePath(
        CurvePath.METHOD.CURVE_BOTH_TO, 
        CurvePoint(stack.t_matrix, x1, y1), 
        CurvePoint(stack.t_matrix, x2, y2), 
        CurvePoint(stack.t_matrix, x3, y3),
    ))
    return stack

# urveto
@PDFCommands.add('v')
def curve_urveto(stack: PDFStateStack, 
        x2: float, y2: float, 
        x3: float, y3: float) -> PDFStateStack:
    stack.curvestacks.append(CurvePath(
        CurvePath.METHOD.CURVE_NEXT_TO, 
        CurvePoint(stack.t_matrix, x2, y2), 
        CurvePoint(stack.t_matrix, x3, y3),
    ))
    return stack

# rveto
@PDFCommands.add('y')
def curve_rveto(stack: PDFStateStack, 
        x1: float, y1: float, 
        x3: float, y3: float) -> PDFStateStack:
    stack.curvestacks.append(CurvePath(
        CurvePath.METHOD.CURVE_FIRST_TO, 
        CurvePoint(stack.t_matrix, x1, y1), 
        CurvePoint(stack.t_matrix, x3, y3)
    ))
    return stack

# closepath
@PDFCommands.add('h')
def curve_close(stack: PDFStateStack) -> PDFStateStack:
    stack.curvestacks.append(CurvePath(CurvePath.METHOD.CLOSE_PATH))
    return stack

# rectangle
@PDFCommands.add('re')
def curve_rect(stack: PDFStateStack, x, y, w, h) -> PDFStateStack:
    stack.curvestacks.extend([
        CurvePath(CurvePath.METHOD.MOVE_TO, CurvePoint(stack.t_matrix, x, y) ),
        CurvePath(CurvePath.METHOD.LINE_TO, CurvePoint(stack.t_matrix, x+w, y) ),
        CurvePath(CurvePath.METHOD.LINE_TO, CurvePoint(stack.t_matrix, x+w, y+h) ),
        CurvePath(CurvePath.METHOD.LINE_TO, CurvePoint(stack.t_matrix, x, y+h) ),
        CurvePath(CurvePath.METHOD.CLOSE_PATH)
    ])
    return stack

# stroke, fill
@PDFCommands.add('S', 'f', 'F', 'B')
def curve_complete_path(stack: PDFStateStack) -> PDFStateStack:
    stack.complete_layout_items.append(make_curve(
        stack.t_matrix,
        stack.graphics.copy(),
        False,
        stack.curvestacks
    ))
    stack.curvestacks = []
    return stack

# sroke, fill-even-odd
@PDFCommands.add('f_a', 'B_a')
def curve_complete_path_evenodd(stack: PDFStateStack) -> PDFStateStack:
    stack.complete_layout_items.append(make_curve(
        stack.t_matrix,
        stack.graphics.copy(),
        True,
        stack.curvestacks
    ))
    stack.curvestacks = []
    return stack

# close-and-stroke (do_h, do_S)
@PDFCommands.add('s', 'b')
def curve_close_complete(stack: PDFStateStack) -> PDFStateStack:
    stack.curvestacks.append(CurvePath(
        CurvePath.METHOD.CLOSE_PATH
    ))
    stack.complete_layout_items.append(make_curve(
        stack.t_matrix,
        stack.graphics.copy(),
        False,
        stack.curvestacks
    ))
    stack.curvestacks = []
    return stack

# close-fill-and-stroke-even-odd
@PDFCommands.add('b_a')
def curve_close_complete_evenodd(stack: PDFStateStack) -> PDFStateStack:
    stack.curvestacks.append(CurvePath(
        CurvePath.METHOD.CLOSE_PATH
    ))
    stack.complete_layout_items.append(make_curve(
        stack.t_matrix,
        stack.graphics.copy(),
        True,
        stack.curvestacks
    ))
    stack.curvestacks = []
    return stack

# close-only (empty path)
@PDFCommands.add('n')
def curve_close_only(stack: PDFStateStack) -> PDFStateStack:
    stack.curvestacks = []
    return stack


# setcolorspace-stroking
@PDFCommands.add('CS')
def set_stroke_colorspace(stack: PDFStateStack, name: str) -> PDFStateStack:
    try:
        stack.graphics.scolspace = stack.colorspace_map[literal_name(name)]
        return stack
    except KeyError:
        raise PDFCommands.InvalidOperation('Undefined ColorSpace: %r' % name)

# setcolorspace-non-strokine
@PDFCommands.add('cs')
def set_nonstroke_colorspace(stack: PDFStateStack, name: str) -> PDFStateStack:
    try:
        stack.graphics.ncolspace = stack.colorspace_map[literal_name(name)]
        return stack
    except KeyError:
        raise PDFCommands.InvalidOperation('Undefined ColorSpace: %r' % name)

# setgray-stroking
@PDFCommands.add('G')
def set_stroke_gray(stack: PDFStateStack, gray: float) -> PDFStateStack:
    stack.graphics.set_stroke_color(
        stack.colorspace_map['DeviceGray'], 
        gray
    )
    return stack

# setgray-non-stroking
@PDFCommands.add('g')
def set_nonstroke_gray(stack: PDFStateStack, gray: float) -> PDFStateStack:
    stack.graphics.set_nostroke_color(
        stack.colorspace_map['DeviceGray'], 
        gray
    )
    return stack


# setrgb-stroking
@PDFCommands.add('RG')
def set_stroke_rgb(stack: PDFStateStack, r, g, b) -> PDFStateStack:
    stack.graphics.set_stroke_color(
        stack.colorspace_map['DeviceRGB'], 
        round(r*255), 
        round(g*255), 
        round(b*255)
    )
    return stack

# setrgb-non-stroking
@PDFCommands.add('rg')
def set_nonstroke_rgb(stack: PDFStateStack, r, g, b) -> PDFStateStack:
    stack.graphics.set_nostroke_color(
        stack.colorspace_map['DeviceRGB'], 
        round(r*255), 
        round(g*255), 
        round(b*255)
    )
    return stack

# setcmyk-stroking
@PDFCommands.add('K')
def set_stroke_cmyk(stack: PDFStateStack, c, m, y, k) -> PDFStateStack:
    stack.graphics.set_stroke_color(
        stack.colorspace_map['DeviceCMYK'], 
        c, m, y, k
    )
    return stack

# setcmyk-non-stroking
@PDFCommands.add('k')
def set_nonstroke_cmyk(stack: PDFStateStack, c, m, y, k) -> PDFStateStack:
    stack.graphics.set_stroke_color(
        stack.colorspace_map['DeviceCMYK'], 
        c, m, y, k
    )
    return stack

@PDFCommands.add('SCN','SC')
def set_stroke_colorspace_custom(stack: PDFStateStack) -> PDFStateStack:
    if stack.graphics.scolspace is None:
        raise PDFCommands.InvalidOperation('No colorspace specified!')
    components = stack.pop(stack.graphics.scolspace.ncomponents)
    stack.graphics.set_stroke_color(
        stack.graphics.scolspace,
        *components
    )
    return stack

@PDFCommands.add('scn','sc')
def set_nonstroke_colorspace_custom(stack: PDFStateStack) -> PDFStateStack:
    if stack.graphics.ncolspace is None:
        raise PDFCommands.InvalidOperation('No colorspace specified!')
    components = stack.pop(stack.graphics.ncolspace.ncomponents)
    stack.graphics.set_nostroke_color(
        stack.graphics.ncolspace,
        *components
    )
    return stack

# begin-text
@PDFCommands.add('BT')
def begin_text(stack: PDFStateStack) -> PDFStateStack:
    stack.text.matrix = MATRIX_IDENTITY
    stack.text.linematrix = [0, 0]
    if stack.current_textblock is None:
        stack.current_textblock = LTTextBlock()
    else:
        raise PDFCommands.InvalidOperation("Last TextBlock did not clear")
    return stack

@PDFCommands.add('ET')
def end_text(stack: PDFStateStack) -> PDFStateStack:
    stack.complete_layout_items.append(stack.current_textblock)
    stack.current_textblock = None
    return stack

# setcharspace
@PDFCommands.add('Tc')
def set_charspace(stack: PDFStateStack, charspace) -> PDFStateStack:
    stack.text.charspace = charspace
    return stack

# setwordspace
@PDFCommands.add('Tw')
def set_wordspace(stack: PDFStateStack, wordspace) -> PDFStateStack:
    stack.text.wordspace = wordspace
    return stack

# textscale
@PDFCommands.add('Tz')
def set_textscale(stack: PDFStateStack, scaling) -> PDFStateStack:
    stack.text.scaling = scaling
    return stack

# setleading
@PDFCommands.add('TL')
def set_text_leading(stack: PDFStateStack, leading) -> PDFStateStack:
    stack.text.leading = -leading
    return stack

# selectfont
@PDFCommands.add('Tf')
def set_font(stack: PDFStateStack, fontid, fontsize) -> PDFStateStack:
    stack.text.fontsize = fontsize
    try:
        stack.text.font = stack.fontmap[literal_name(fontid)]
        return stack
    except KeyError:
        raise PDFCommands.InvalidOperation('Undefined Font id: %r' % fontid)

# setrendering
@PDFCommands.add('Tr')
def set_text_rendering(stack: PDFStateStack, render) -> PDFStateStack:
    stack.text.render = render
    return stack

# settextrise
@PDFCommands.add('Ts')
def set_textrise(stack: PDFStateStack, rise) -> PDFStateStack:
    stack.text.rise = rise
    return stack

# text-move
@PDFCommands.add('Td')
def move_text_x(stack: PDFStateStack, tx, ty) -> PDFStateStack:
    (a, b, c, d, e, f) = stack.text.matrix
    stack.text.matrix = (a, b, c, d, tx*a+ty*c+e, tx*b+ty*d+f)
    stack.text.linematrix = [0, 0]
    return stack

# text-move
@PDFCommands.add('TD')
def move_text_y(stack: PDFStateStack, tx, ty) -> PDFStateStack:
    (a, b, c, d, e, f) = stack.text.matrix
    stack.text.matrix = (a, b, c, d, tx*a+ty*c+e, tx*b+ty*d+f)
    stack.text.leading = ty
    stack.text.linematrix = [0, 0]
    return stack

# textmatrix
@PDFCommands.add('Tm')
def set_text_matrix(stack: PDFStateStack, a, b, c, d, e, f) -> PDFStateStack:
    stack.text.matrix = (a, b, c, d, e, f)
    stack.text.linematrix = [0, 0]
    return stack

# nextline
@PDFCommands.add('T_a')
def nextline(stack: PDFStateStack) -> PDFStateStack:
    (a, b, c, d, e, f) = stack.text.matrix
    stack.text.matrix = (a, b, c, d, stack.text.leading*c+e, stack.text.leading*d+f)
    stack.text.linematrix = [0, 0]
    return stack

# show-pos
@PDFCommands.add('TJ')
def add_char_blocks(stack: PDFStateStack, seq: bytearray) -> PDFStateStack:
    if stack.text.font is None:
        raise PDFCommands.InvalidOperation("No Font Specified")
    if stack.current_textblock is None:
        raise PDFCommands.InvalidOperation("No TextBlock initilized")
    stack.current_textblock.add_char_block(
        seq,
        stack.t_matrix,
        stack.text.copy(),
        stack.graphics.ncolor.copy()
    )
    return stack

# show
@PDFCommands.add('Tj')
def add_char_block(stack: PDFStateStack, b: bytes) -> PDFStateStack:
    return add_char_blocks(stack, [b])

# quote
@PDFCommands.add('_q')
def add_quoted_char_blocks(stack: PDFStateStack, b: bytes) -> PDFStateStack:
    return add_char_blocks(nextline(stack), [b])

# doublequote
@PDFCommands.add('_w')
def add_dbquoted_char_blocks(stack: PDFStateStack, wordspace, charspace, b) -> PDFStateStack:
    stack.text.wordspace = wordspace
    stack.text.charspace = charspace
    return add_char_blocks(stack, [b])

@PDFCommands.add('EI')
def insert_image(stack: PDFStateStack, obj) -> PDFStateStack:
    if 'W' in obj and 'H' in obj:
        stack.complete_layout_items.append(make_image(
            obj,  stack.t_matrix
        ))
    return stack

# invoke an XObject
@PDFCommands.add('Do')
def insert_xobject(stack: PDFStateStack, xobjid) -> PDFStateStack:
    xobjid = literal_name(xobjid)
    try:
        xobj = PDFStream.validated_stream(stack.xobjmap[xobjid])
    except KeyError:
        raise PDFCommands.InvalidOperation('Undefined xobject id: %r' % xobjid)
    # log.info('Processing xobj: %r', xobj)
    subtype = xobj.get('Subtype')
    if subtype is LITERAL_FORM and 'BBox' in xobj:
        bbox = list_value(xobj['BBox'])
        matrix = list_value(xobj.get('Matrix', MATRIX_IDENTITY))
        # According to PDF reference 1.7 section 4.9.1, XObjects in
        # earlier PDFs (prior to v1.2) use the page's Resources entry
        # instead of having their own Resources entry.
        xobjres = xobj.get('Resources')
        resources = dict_value(xobjres) if xobjres else stack.resources.copy()
        stack.complete_layout_items.append(make_xobject(
            obj=xobj, 
            bbox=bbox, 
            ctm=stack.t_matrix, 
            matrix=matrix, 
            resources=resources
        ))
    elif subtype is LITERAL_IMAGE and 'Width' in xobj and 'Height' in xobj:
        stack.complete_layout_items.append(make_image(
            xobj,  stack.t_matrix
        ))
    else:
        # unsupported xobject type.
        pass
    return stack

