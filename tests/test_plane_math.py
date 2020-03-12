from tin2dem.plane_math import equation_plane, solve_z, norm_z


def test_equation():
    def test_eq(xyz, abcd):
        (x, y, z) = xyz
        (a, b, c, d) = abcd
        return a * x + b * y + c * z + d
    points = [
        (-1, 2, 1),
        (0, -3, 2),
        (1, 1, -4)
    ]
    eq_coef = equation_plane(*points)
    assert eq_coef == (26, 7, 9, 3)

    # print("Equation of plane is {}x + {}y + {}z + {} = 0".format(eq_coef[0], eq_coef[1], eq_coef[2], eq_coef[3]))
    for p in points:
        assert test_eq(p, eq_coef) == 0


def test_solve_z():
    points = [
        (1, 2, 4),
        (3, 6, 2),
        (1, 1, 2)
    ]
    eq_coef = equation_plane(*points)
    for p in points:
        assert solve_z((p[0], p[1]), norm_z(eq_coef)) == p[2]
