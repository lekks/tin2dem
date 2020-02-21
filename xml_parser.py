import logging
import re
import xml.etree.ElementTree as etree

NS_TAG = re.compile("{http://www\.landxml\.org/schema/LandXML-\d\.\d}(\w+)")

log = logging.getLogger("TIN XML parser")


def parse_xml(filename):
    def is_landxml_tag(tag, name):
        return NS_TAG.findall(tag)[0] == name

    surfaces = []
    with open(filename, "r") as xmlfile:
        for event, elem in etree.iterparse(xmlfile, events=('start', 'end')):
            if event == "start":
                if is_landxml_tag(elem.tag, "Surface"):
                    surfaces.append({'P': {}, 'F': []})
            elif event == "end" and surfaces:  # at the start "text" field is undefined
                if is_landxml_tag(elem.tag, "P"):
                    coord = list(map(float, elem.text.split()))
                    surfaces[-1]['P'][int(elem.attrib["id"])] = coord
                elif is_landxml_tag(elem.tag, "F"):
                    # http://www.landxml.org/schema/LandXML-1.2/documentation/LandXML-1.2Doc_F.html
                    if "i" in elem.attrib and elem.attrib["i"] == "1":
                        log.debug("invisible face")
                    else:
                        points = list(map(int, elem.text.split()))
                        surfaces[-1]['F'].append(points)
    log.info("Found %s surfaces", len(surfaces))
    return surfaces
