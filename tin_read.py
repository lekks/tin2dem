import logging

from xml_parser import parse_xml

log = logging.getLogger("TIN model")


class Surface:
    def __init__(self):
        self.min_vertex = [None, None, None]
        self.max_vertex = [None, None, None]
        self.vertices = list()
        self.faces = list()
        self.surfaces = 0

    def add_vertex(self, vid, coord):
        log.debug("Point {}=({})".format(vid, coord))
        assert len(coord) == 3
        for i in (0, 1, 2):
            if self.min_vertex[i] is None or self.min_vertex[i] > coord[i]:
                self.min_vertex[i] = coord[i]
            if self.max_vertex[i] is None or self.max_vertex[i] < coord[i]:
                self.max_vertex[i] = coord[i]
        self.vertices.append(tuple([vid] + coord))

    def add_face(self, points):
        log.debug("Face {}".format(points))
        assert len(points) == 3
        self.faces.append(points)

    def from_collections(self, vertices, faces):
        for i, v in vertices.items():
            self.add_vertex(i, v)
        for f in faces:
            self.add_face(f)
        return self

    def shift_origin(self):
        x_shift = self.min_vertex[0]
        y_shift = self.min_vertex[1]
        for i, v in enumerate(self.vertices):
            self.vertices[i] = (v[0], v[1] - x_shift, v[2] - y_shift, v[3])
        self.max_vertex = (self.max_vertex[0] - x_shift, self.max_vertex[1] - y_shift, self.max_vertex[2])
        self.min_vertex = (self.min_vertex[0] - x_shift, self.min_vertex[1] - y_shift, self.min_vertex[2])
        return x_shift, y_shift

    def get_envelope(self):
        return self.min_vertex[0], self.max_vertex[0], self.min_vertex[1], self.max_vertex[1]

    def read_tin(self, filename, select_surface, swap_xy=False):
        surfaces_list = parse_xml(filename)
        for i, surface in enumerate(surfaces_list):
            if select_surface is None or i == select_surface:
                for vid, coords in surface['P'].items():
                    if not swap_xy:
                        coords[0], coords[1] = coords[1], coords[0]
                    self.add_vertex(vid, coords)

                for f in surface['F']:
                    self.add_face(f)
        self.surfaces = len(surfaces_list)
