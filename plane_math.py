from __future__ import division


# https://www.geeksforgeeks.org/program-to-find-equation-of-a-plane-passing-through-3-points/
def equation_plane((x1, y1, z1), (x2, y2, z2), (x3, y3, z3)):
    a1 = x2 - x1
    b1 = y2 - y1
    c1 = z2 - z1
    a2 = x3 - x1
    b2 = y3 - y1
    c2 = z3 - z1
    a = b1 * c2 - b2 * c1
    b = a2 * c1 - a1 * c2
    c = a1 * b2 - b1 * a2
    d = (- a * x1 - b * y1 - c * z1)
    return a, b, c, d


def norm_z((a, b, c, d)):
    if not c:
        raise ArithmeticError("Plane is orthogonal")
    return -a / c, -b / c, -d / c


def solve_z((x, y), (za, zb, zc)):
    return za * x + zb * y + zc
