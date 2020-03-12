from tin2dem.dem_geo import split_dem, DemInfo
import pytest


def test_simple_geotransform():
    bbox = 100, 200, 100, 200
    dem = DemInfo.from_envelope(*bbox, pix_size=1, margins=0)

    expected_gt = [100, 1, 0, 200, 0, -1]
    # print dem.gt
    # print dem.bbox
    assert dem.width == 100
    assert dem.height == 100

    for exp, real in zip(expected_gt, dem.gt):
        assert exp == pytest.approx(real, abs=0.001)

    for exp, real in zip(bbox, dem.bbox()):
        assert exp == pytest.approx(real, abs=0.001)


def test_real_geotransform():
    bbox = -13043520.255, -13043367.381, 3869089.498, 3869242.372
    dem = DemInfo.from_envelope(*bbox, pix_size=0.14929107, margins=0)
    expected_gt = [-13043520.2546954303979874, 0.14929107, 0.0, 3869242.3717958591878414, 0.0, -0.14929107]

    assert dem.width == 1024
    assert dem.height == 1024
    for exp, real in zip(expected_gt, dem.gt):
        assert exp == pytest.approx(real, abs=0.001)

    for exp, real in zip(bbox, dem.bbox()):
        assert exp == pytest.approx(real, abs=0.001)


def test_split_dem():
    dem = DemInfo.from_envelope(100, 200, 100, 200, pix_size=1, margins=0)
    chunks = tuple(split_dem(dem, 51, 21))
    assert len(chunks) == 10
    expected_gt = [[100, 1, 0, 200, 0, -1],
                   [100, 1, 0, 179, 0, -1],
                   [100, 1, 0, 158, 0, -1],
                   [100, 1, 0, 137, 0, -1],
                   [100, 1, 0, 116, 0, -1],
                   [151, 1, 0, 200, 0, -1],
                   [151, 1, 0, 179, 0, -1],
                   [151, 1, 0, 158, 0, -1],
                   [151, 1, 0, 137, 0, -1],
                   [151, 1, 0, 116, 0, -1]]
    for i, chunk in enumerate(chunks):
        # print("{}-{},{}-{}:{}".format(chunk.offset_col, chunk.offset_col + chunk.width - 1, chunk.offset_row, chunk.offset_row + chunk.height - 1, chunk.gt))
        assert chunk.pixel_coord(1, 1) == dem.pixel_coord(chunk.offset_col + 1, chunk.offset_row + 1)
        assert chunk.offset_col+chunk.width < 200
        assert chunk.offset_row+chunk.height < 200
        assert chunk.gt == expected_gt[i]

