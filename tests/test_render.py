from tin2dem.dem_geo import DemInfo
from tin2dem.render import Render
from tin2dem.surface import Surface
import pytest


@pytest.fixture
def test_surface():
    vertices = {
        1: [1.0,   5.0,  2.0],
        2: [3.0,   5.0,  2.0],
        3: [2.0,   2.0,  2.0],
        4: [5.0,   2.0,  2.0],
        5: [9.0,   2.0,  2.0],
        6: [12.0,  1.0,  2.0],
        7: [11.0, -3.0,  2.0],
        8: [2.0,  -3.0,  2.0],
        9: [0.0,  -3.0,  2.0],
    }

    faces = [
        (1, 2, 3),
        (2, 4, 3),
        (3, 4, 8),
        (4, 5, 7),
        (6, 5, 7),
        (4, 8, 7),
        (3, 8, 9),
        (1, 3, 9)
    ]
    return vertices, faces

@pytest.fixture
def cad_surface():
    vertices = {
        0: [0, 0, 0],
        1: [0, 3, 18],
        2: [0, 6, 0],
        3: [3, 0, 0],
        4: [3, 3, 18],
        5: [3, 6, 0],
    }

    faces = [
        (0, 1, 3),
        (3, 4, 1),
        (1, 2, 4),
        (2, 5, 4)
    ]
    return vertices, faces

def test_cad_compatible(cad_surface):
    vertices, faces = cad_surface
    surface = Surface().from_collections(vertices, faces)
    render = Render(surface)
    # TODO check result is same as cad result




def test_filter(test_surface):
    vertices, faces = test_surface

    bounds = [3, 8, -2, 3] #wesn

    expected = [0, 1, 2, 3, 5]

    surface = Surface().from_collections(vertices, faces)
    dem = DemInfo.from_envelope(*bounds, pix_size=1)
    render = Render(surface)
    result = render._select_filtered(render.filter_bounds(dem))

    assert list(result) == expected

def test_choose_face(test_surface):
    vertices, faces = test_surface

    bounds = [3, 8, -2, 3]  # wesn

    expected = [
        [2, 2, -1, -1, -1],
        [3, 3, 6, 4, 4],
        [3, 6, 6, 6, 4],
        [6, 6, 6, 6, 6],
        [6, 6, 6, 6, 6]
    ]

    surface = Surface().from_collections(vertices, faces)
    dem = DemInfo.from_envelope(*bounds, pix_size=1, margins=0)
    result, debug = Render(surface).render_dem(dem)
    assert list(map(list, debug)) == expected
