import pygraphviz
import numpy as np


def split_pos(node):
    x = float(node.attr["pos"].split(",")[0])
    y = float(node.attr["pos"].split(",")[1].split("!")[0])
    return x, y


def put_on_left_edge(graph, target_node, moving_node, offset_y=0):
    ...
    # Get top left corner of target
    tnode = graph.get_node(target_node)
    x, y = split_pos(tnode)

    xe = x - float(tnode.attr["width"]) / 2
    ye = y + float(tnode.attr["height"]) / 2

    print(xe, ye)

    # Shift to center
    mnode = graph.get_node(moving_node)
    xe = xe + float(mnode.attr["width"]) / 2
    ye = ye + float(mnode.attr["height"]) / 2

    mnode.attr["pos"] = f"{xe},{ye+offset_y}!"


def add_fpga_carrier(graph, border_with=0.25):

    print("------------")

    # Calculate outer box
    y_edge = ["NA", "NA"]
    x_edge = ["NA", "NA"]
    for node in graph.nodes_iter():
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

        print(pos, lx, rx, by, ty)

        y_edge[0] = np.min([by, y_edge[0]])
        y_edge[1] = np.max([ty, y_edge[1]])

    print("------------")

    height = y_edge[1] - y_edge[0]
    width = x_edge[1] - x_edge[0]

    print(x_edge)
    print(y_edge)

    x_pos = x_edge[1] - width / 2
    y_pos = y_edge[1] - height / 2
    pos = f"{x_pos},{y_pos}!"
    print(pos)

    height = height + border_with * 2
    width = width + border_with * 2

    graph.add_node(
        "BOX",
        shape="rect",
        pos=pos,
        width=width,
        height=height,
        color="red",
        fixedsize="true",
    )


def add_axi_interconnect(graph, rx_nodes, tx_nodes, width, height, dma_name="DMA"):

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
        node = graph.get_node(nodename)
        if edge == "NA":
            edge = node.attr["pos"].split(",")[0]
        e = node.attr["pos"].split(",")[0]
        if edge != e:
            raise Exception(f"{node.name} not aligned to {edge} {e}")
        y = node.attr["pos"].split(",")[1]
        y = float(y.split("!")[0])
        ys.append(y)

    # Determine location
    print(ys)
    top = np.max(ys)
    bottom = np.min(ys)

    height = float(node.attr["height"])
    x = float(edge) - 3
    y = (top - bottom) / 2

    height = height + y * 2

    pos = f"{x},{y}!"

    graph.add_node(
        "AXI-INTERCONNECT",
        shape="rect",
        pos=pos,
        width=str(width),
        height=height,
        color="green",
        fixedsize="true",
    )

    return y, height


def add_path(graph, path, x_spacing=1, y_level=0, extra=None, reverse_connect=False):

    i = 0
    for item in path:
        classname = item.replace("-", "_").replace(" ", "_")
        if extra:
            print(extra)
            graph.add_node(item, pos=f"{i},{y_level}!", **extra)

            # graph.node(item, item, pos=f"{i},{y_level}!", **extra)
        else:
            graph.node(item, item, pos=f"{i},{y_level}!")
        i += x_spacing
        n = graph.get_node(item)
        n.attr["class"] = classname

    # Connect
    if reverse_connect:
        print(path)
        path.reverse()
        print(path)
    last = len(path)
    for i in range(last - 1):
        # graph.edge(path[i], path[i + 1])
        graph.add_edge(path[i], path[i + 1])


def create_lvds_cmos():

    name = "FMComms2"
    comment = f"{name} reference design"
    # g = pygraphviz.Digraph(name, comment=comment, engine="neato")
    g = pygraphviz.AGraph()

    # g.attr('node', shape='rect', fixedsize='true', width='0.9')

    tx = ["AXI_DMA_TX", "UPACK", "CUSTOM IP TX", "FIFO TX", "INTER_TX"]
    rx = ["INTER_RX", "FIFO RX", "CUSTOM IP RX", "CPACK", "AXI_DMA_RX"]
    rx.reverse()

    width = 2

    # g.node("A", "King Simba", pos="0,2!")
    # g.node("B", "King Arthur", pos="1,1!")
    add_path(
        g,
        tx,
        x_spacing=2.5,
        y_level=0,
        extra={
            "shape": "rect",
            "width": str(width),
            "height": "1",
            "fixedsize": "true",
        },
    )

    add_path(
        g,
        rx,
        x_spacing=2.5,
        y_level=3,
        extra={
            "shape": "rect",
            "width": str(width),
            "height": "1",
            "fixedsize": "true",
        },
        reverse_connect=True,
    )

    ya, height = add_axi_interconnect(g, rx, tx, width=width, height=1)

    # Update Interface core to be similar
    n = g.get_node("INTER_TX")
    n.attr["label"] = ""
    n.attr["style"] = "invis"
    pos = n.attr["pos"]
    x = pos.split(",")[0]
    # n.attr["pos"] = f"{x},{ya}!"
    # n.attr["height"] = height
    n = g.get_node("INTER_RX")
    n.attr["label"] = ""
    n.attr["style"] = "invis"

    g.add_node(
        "AXI_AD9361",
        shape="rect",
        width=str(width),
        pos=f"{x},{ya}!",
        height=height,
        fixedsize="true",
    )

    g.add_node(
        "MicroBlaze/Zynq",
        shape="rect",
        width=str(width),
        pos=f"{0},{6}!",
        height=1,
        fixedsize="true",
    )

    put_on_left_edge(g, "AXI-INTERCONNECT", "MicroBlaze/Zynq", offset_y=1)

    add_fpga_carrier(g)

    # g.attr("AXI_AD9361", pos)
    return g

    # g.render(directory="doctest-output", view=True)


if __name__ == "__main__":
    g = create_lvds_cmos()
    g.draw("out.svg", prog="neato")
