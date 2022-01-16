import pathlib
import sys

import numpy as np
from pygraphviz import AGraph
from loguru import logger

from grafic.process_xml import process_xml
import xml.etree.ElementTree as ET

config = {
    "handlers": [
        {"sink": sys.stdout, "format": "{time} - {level} - {message}"},
        # {"sink": "file.log", "serialize": True},
    ],
    "extra": {"user": "someone"},
}
logger.configure(**config)


class grafic(AGraph, process_xml):

    _svg_output_file = None
    _post_process_queue = []
    _enable_logging = False
    logger = logger

    def get_graph_corner(self, corner="nw"):
        """
        Get the graph corner
        """
        # Get the graph corner
        ys = []
        xs = []
        overall_left_edge = "NA"
        overall_right_edge = "NA"
        overall_top = "NA"
        overall_bottom = "NA"
        for node in self.nodes():
            # node = self.get_node(nodename)
            x = node.attr["pos"].split(",")[0]
            y = node.attr["pos"].split(",")[1]
            y = float(y.split("!")[0])
            xs.append(float(x))
            ys.append(y)

            w = node.attr["width"]
            left_edge = float(x) - float(w) / 2
            if overall_left_edge == "NA":
                overall_left_edge = left_edge
            overall_left_edge = np.min([left_edge, overall_left_edge])

            right_edge = float(x) + float(w) / 2
            if overall_right_edge == "NA":
                overall_right_edge = right_edge
            overall_right_edge = np.max([right_edge, overall_right_edge])

            h = node.attr["height"]
            top = float(y) + float(h) / 2
            if overall_top == "NA":
                overall_top = top
            overall_top = np.max([top, overall_top])

            bottom = float(y) - float(h) / 2
            if overall_bottom == "NA":
                overall_bottom = bottom
            overall_bottom = np.min([bottom, overall_bottom])

        if corner == "sw":
            return overall_left_edge, overall_bottom
        elif corner == "nw":
            return overall_left_edge, overall_top
        elif corner == "se":
            return overall_right_edge, overall_bottom
        elif corner == "ne":
            return overall_right_edge, overall_top
        else:
            raise ValueError("Invalid corner")

    def add_node_with_class(self, n, **kwargs):
        super(grafic, self).add_node(n, **kwargs)
        print("nodename", n)
        n = self.get_node(n)
        n.attr["class"] = n

    def draw(self, *args, **kwargs):
        # Grab filename
        print(kwargs)
        print(args)
        self._svg_output_file = kwargs.get("path")
        if self._svg_output_file is None:
            self._svg_output_file = args[0]
        file_extension = pathlib.Path(self._svg_output_file).suffix
        if file_extension != ".svg":
            raise ValueError("Invalid file extension. Must be .svg")
        super(grafic, self).draw(*args, **kwargs)
        self._post_process_svg()

    def _post_process_svg(self):
        self.tree = ET.parse(self._svg_output_file)

        # get root element
        root = self.tree.getroot()

        self.xmlgraph = root[0]
        for task in self._post_process_queue:
            logger.debug(task)
            getattr(self, task["task"])(**task["args"])
        self.tree.write(self._svg_output_file)
