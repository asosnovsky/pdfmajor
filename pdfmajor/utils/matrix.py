##  Matrix operations
##
MATRIX_IDENTITY = (1, 0, 0, 1, 0, 0)

def mult_matrix(m1, m0):
    (a1, b1, c1, d1, e1, f1) = m1
    (a0, b0, c0, d0, e0, f0) = m0
    """Returns the multiplication of two matrices."""
    return (a0*a1+c0*b1,    b0*a1+d0*b1,
            a0*c1+c0*d1,    b0*c1+d0*d1,
            a0*e1+c0*f1+e0, b0*e1+d0*f1+f0)


def translate_matrix(m, v):
    """Translates a matrix by (x, y)."""
    (a, b, c, d, e, f) = m
    (x, y) = v
    return (a, b, c, d, x*a+y*c+e, x*b+y*d+f)


def apply_matrix_pt(m, v):
    (a, b, c, d, e, f) = m
    (x, y) = v
    """Applies a matrix to a point."""
    return (a*x+c*y+e, b*x+d*y+f)


def apply_matrix_norm(m, v):
    """Equivalent to apply_matrix_pt(M, (p,q)) - apply_matrix_pt(M, (0,0))"""
    (a, b, c, d, _, _) = m
    (p, q) = v
    return (a*p+c*q, b*p+d*q)

def matrix2str(m):
    (a, b, c, d, e, f) = m
    return '[%.2f,%.2f,%.2f,%.2f, (%.2f,%.2f)]' % (a, b, c, d, e, f)
