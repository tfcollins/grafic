import xml.etree.ElementTree as ET


class process_xml:

    _svg_output_file = None

    def rotate(self, angle, node_name, element="text"):
        # Check if node exists

        # Add to post process queue
        args = {"angle": angle, "node_name": node_name, "element": element}
        d = {"task": "_do_rotate", "args": args}
        self._post_process_queue.append(d)
        # self._do_rotate(angle=angle)

    def _do_rotate(self, angle, node_name, element="text"):
        self.logger.debug(f"Rotating {node_name} by {angle}")

        for child in self.xmlgraph.getchildren():
            # FIXME HANDLE BY ID NOT CLASSNAME
            # "id" in child.attrib and
            if "class" in child.attrib:
                if node_name in child.attrib["class"].split(" "):
                    for cchild in child.getchildren():
                        if cchild.tag == "{http://www.w3.org/2000/svg}" + str(element):
                            x = cchild.attrib["x"]
                            y = cchild.attrib["y"]
                            cchild.attrib["transform"] = f"rotate({angle} {x} {y})"
                            # print(cchild.attrib['transform'])
                            return
        raise Exception(f"Node {node_name} not found")
