import logging
import sys
import xml.etree.ElementTree as etree

log = logging.getLogger("Surface reader")


class Surface:
    def __init__(self):
        self.min_vertex = [None, None, None]
        self.max_vertex = [None, None, None]
        self.vertices = list()
        self.faces = list()

    def add_vertex(self, vid, coord):
        log.debug("Point {}=({})".format(vid, coord))
        assert len(coord) == 3
        for i in (0, 1, 2):
            if self.min_vertex[i] is None or self.min_vertex[i] > coord[i]:
                self.min_vertex[i] = coord[i]
            if self.max_vertex[i] is None or self.max_vertex[i] < coord[i]:
                self.max_vertex[i] = coord[i]
        self.vertices.append(tuple([vid]+list(coord)))

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

    def read_tin(self, filename, swap = False):
        # http://boscoh.com/programming/reading-xml-serially.html
        # https://docs.python.org/2/library/xml.etree.elementtree.html#tutorial

        def is_landxml_tag(tag, name):
            return tag == "{http://www.landxml.org/schema/LandXML-1.2}" + name

        # todo test elem.clear() on large files
        surfaces = 0
        with open(filename, "r") as xmlfile:
            for event, elem in etree.iterparse(xmlfile, events=('start', 'end')):
                if event == "start":
                    if is_landxml_tag(elem.tag, "Surface"):
                        surfaces += 1
                elif event == "end": #at the start "text" field is undefined
                    if is_landxml_tag(elem.tag, "P"):
                        coord = list(map(float, elem.text.split()))
                        if not swap:
                            coord[0], coord[1] = coord[1], coord[0]
                        self.add_vertex(int(elem.attrib["id"]), coord)
                    elif is_landxml_tag(elem.tag, "F"):
                        #http://www.landxml.org/schema/LandXML-1.2/documentation/LandXML-1.2Doc_F.html
                        if "i" in elem.attrib and elem.attrib["i"] == "1":
                            log.debug("invisible face")
                        else:
                            points = tuple(map(int, elem.text.split()))
                            self.add_face(points)
        log.info("Found %s surfaces", surfaces)
        assert surfaces == 1, "Found %s surfaces, supporting only 1"
        return self

    def get_envelope(self):
        return self.min_vertex[0], self.max_vertex[0], self.min_vertex[1], self.max_vertex[1]

def debug_small():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    surface = Surface()
    surface.read_tin("test/2slopesT1.xml")
    #surface.read_tin("test/sky_crop.xml")


def run_large(file_name="test/russell.xml"):
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log.info("Let`s read tinn {}".format(file_name))
    surface = Surface()
    surface.read_tin(file_name)
    log.info("{} points".format(len(surface.vertices)))
    log.info("{} faces".format(len(surface.faces)))
    log.info("Min corner is {}".format(surface.min_vertex))
    log.info("Max corner is {}".format(surface.max_vertex))


if __name__ == '__main__':
    run_large()
