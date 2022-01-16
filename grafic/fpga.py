from grafic import grafic
import numpy as np


class fpga_reference_designs(grafic):
    def add_overlay_node(self, node_names, overlay_node_name, make_invisible=False):
        if not isinstance(node_names, list):
            node_names = [node_names]
        # Check to make sure all nodes are aligned
        edge = "NA"
        ys = []
        xs = []
        overall_left_edge = "NA"
        overall_right_edge = "NA"
        for nodename in node_names:
            node = self.get_node(nodename)
            if make_invisible:
                node.attr["label"] = ""
                node.attr["style"] = "invis"
            # if edge == "NA":
            #     edge = node.attr["pos"].split(",")[0]
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

        # Determine location
        print(ys)
        top = np.max(ys)
        bottom = np.min(ys)

        height = float(node.attr["height"])
        # x = float(edge) - 3
        x = (np.max(xs) + np.min(xs)) / 2
        y = (top - bottom) / 2

        height = height + y * 2

        print(overall_right_edge, overall_left_edge)
        width = overall_right_edge - overall_left_edge

        pos = f"{x},{y}!"

        self.add_node(
            overlay_node_name,
            shape="rect",
            pos=pos,
            width=str(width),
            height=height,
            # color="green",
            fixedsize="true",
        )
        return x, y, width, height

    def add_overlay_node_OLD(self, width, height, ya):
        n = self.get_node("INTER_TX")
        n.attr["label"] = ""
        n.attr["style"] = "invis"
        pos = n.attr["pos"]
        x = pos.split(",")[0]
        # n.attr["pos"] = f"{x},{ya}!"
        # n.attr["height"] = height
        n = self.get_node("INTER_RX")
        n.attr["label"] = ""
        n.attr["style"] = "invis"

        self.add_node(
            "AXI_AD9361",
            shape="rect",
            width=str(width),
            pos=f"{x},{ya}!",
            height=height,
            fixedsize="true",
        )

    def split_pos(self, node):
        x = float(node.attr["pos"].split(",")[0])
        y = float(node.attr["pos"].split(",")[1].split("!")[0])
        return x, y

    def put_on_left_edge(self, target_node, moving_node, offset_y=0):
        """Align node to left top corner of target node"""
        # Get top left corner of target
        tnode = self.get_node(target_node)
        x, y = self.split_pos(tnode)

        xe = x - float(tnode.attr["width"]) / 2
        ye = y + float(tnode.attr["height"]) / 2

        # Shift to center
        mnode = self.get_node(moving_node)
        xe = xe + float(mnode.attr["width"]) / 2
        ye = ye + float(mnode.attr["height"]) / 2

        mnode.attr["pos"] = f"{xe},{ye+offset_y}!"

    def add_path(self, path, x_spacing=1, y_level=0, extra=None, reverse_connect=False):

        i = 0
        for item in path:
            classname = item.replace("-", "_").replace(" ", "_")
            if extra:
                # print(extra)
                self.add_node(item, pos=f"{i},{y_level}!", **extra)

                # graph.node(item, item, pos=f"{i},{y_level}!", **extra)
            else:
                self.node(item, item, pos=f"{i},{y_level}!")
            i += x_spacing
            n = self.get_node(item)
            n.attr["class"] = classname

        # Connect
        if reverse_connect:
            # print(path)
            path.reverse()
            # print(path)
        last = len(path)
        for i in range(last - 1):
            # graph.edge(path[i], path[i + 1])
            self.add_edge(path[i], path[i + 1])
            # e = self.get_edge(path[i], path[i + 1])
            # print(f"{path[i]} -> {path[i + 1]}")
            # e.attr["shape"] = "box"
            # e = self.get_edge(path[i], path[i + 1])
            # print(f"{e.attr['shape']=}")

    def add_fpga_carrier(self, label="", border_with=0.25):

        print("------------")

        # Calculate outer box
        y_edge = ["NA", "NA"]
        x_edge = ["NA", "NA"]
        for node in self.nodes_iter():
            pos = node.attr["pos"]
            x = float(pos.split(",")[0])
            y = float(pos.split(",")[1].split("!")[0])
            w = float(node.attr["width"])
            h = float(node.attr["height"])

            # assert w == 1.0, str(w)

            lx = x - w / 2
            rx = x + w / 2
            if x_edge[0] == "NA":
                x_edge[0] = lx
            if x_edge[1] == "NA":
                x_edge[1] = rx

            x_edge[0] = np.min([lx, x_edge[0]])
            x_edge[1] = np.max([rx, x_edge[1]])

            ty = y + h / 2
            by = y - h / 2

            if y_edge[0] == "NA":
                y_edge[0] = by
            if y_edge[1] == "NA":
                y_edge[1] = ty

            # print(pos, lx, rx, by, ty)

            y_edge[0] = np.min([by, y_edge[0]])
            y_edge[1] = np.max([ty, y_edge[1]])

        # print("------------")

        height = y_edge[1] - y_edge[0]
        width = x_edge[1] - x_edge[0]

        # print(x_edge)
        # print(y_edge)

        x_pos = x_edge[1] - width / 2
        y_pos = y_edge[1] - height / 2
        pos = f"{x_pos},{y_pos}!"
        # print(pos)

        height = height + border_with * 2
        width = width + border_with * 2

        self.add_node(
            "CARRIER",
            shape="rect",
            pos=pos,
            width=width,
            height=height,
            color="red",
            fixedsize="true",
            label=label,
        )

    def add_axi_interconnect(self, rx_nodes, tx_nodes, width, height, dma_name="DMA"):

        if not isinstance(rx_nodes, list):
            rx_nodes = [rx_nodes]
        if not isinstance(tx_nodes, list):
            tx_nodes = [tx_nodes]
        # Check to make sure all nodes are aligned
        edge = "NA"
        ys = []
        for nodename in rx_nodes + tx_nodes:
            if dma_name not in nodename:
                continue
            node = self.get_node(nodename)
            if edge == "NA":
                edge = node.attr["pos"].split(",")[0]
            e = node.attr["pos"].split(",")[0]
            if edge != e:
                raise Exception(f"{node.name} not aligned to {edge} {e}")
            y = node.attr["pos"].split(",")[1]
            y = float(y.split("!")[0])
            ys.append(y)

        # Determine location
        # print(ys)
        top = np.max(ys)
        bottom = np.min(ys)

        height = float(node.attr["height"])
        x = float(edge) - 3
        y = (top - bottom) / 2

        height = height + y * 2

        pos = f"{x},{y}!"

        self.add_node(
            "AXI-INTERCONNECT",
            shape="rect",
            pos=pos,
            width=str(width),
            height=height,
            color="green",
            fixedsize="true",
        )

        return y, height

    def mode_node_asside(self, node_to_move, target_node, side):
        """
        Move node to the side of target node
        """
        node = self.get_node(node_to_move)
        w = float(node.attr["width"])
        h = float(node.attr["height"])
        target = self.get_node(target_node)
        xt, yt = self.split_pos(target)
        wt = float(target.attr["width"])
        ht = float(target.attr["height"])

        if side == "left":
            x = xt - wt / 2 - w / 2
            y = yt
        elif side == "right":
            x = xt + wt / 2 + w / 2
            y = yt
        elif side == "top":
            x = xt
            y = yt + ht / 2 + h / 2
        elif side == "bottom":
            x = xt
            y = yt - ht / 2 - h / 2
        else:
            raise Exception(f"Unknown side {side}")

        pos = f"{x},{y}!"
        node.attr["pos"] = pos
