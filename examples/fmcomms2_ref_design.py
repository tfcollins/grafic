import grafic

fpga = grafic.fpga_reference_designs(directed=True, strict=False)

# Add data paths
tx = ["AXI_INTER_TX", "AXI_DMA_TX", "UPACK", "CUSTOM IP TX", "FIFO TX", "INTER_TX"]
rx = ["INTER_RX", "FIFO RX", "CUSTOM IP RX", "CPACK", "AXI_DMA_RX", "AXI_INTER_RX"]
rx.reverse()

width = 2

fpga.add_path(
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

fpga.add_path(
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

fpga.add_overlay_node(["INTER_RX", "INTER_TX"], "AXI_AD9361", True)


# Add memory interconnect
ya, height = fpga.add_axi_interconnect(rx, tx, width=width, height=1)
fpga.add_overlay_node(["AXI_INTER_RX", "AXI_INTER_TX"], "AXI-INTERCONNECT", True)


# Add ARM processor representation
fpga.add_node_with_class(
    "MicroBlaze/Zynq",
    shape="rect",
    width=str(width),
    pos=f"{0},{6}!",
    height=1,
    fixedsize="true",
)
fpga.put_on_left_edge("AXI-INTERCONNECT", "MicroBlaze/Zynq", offset_y=1)

cfg = {
    "shape": "rect",
    "width": str(width / 4),
    "pos": f"{0},{0}!",
    "height": 1,
    "fixedsize": "true",
}

peripherials = ["Timer", "Interrupts", "Ethernet", "UART", "I2C", "SPI"]
for i, p in enumerate(peripherials):
    fpga.add_node_with_class(p, **cfg)
    if i == 0:
        fpga.mode_node_asside(p, "MicroBlaze/Zynq", "right")
    else:
        fpga.mode_node_asside(p, peripherials[i - 1], "right")
    fpga.rotate(node_name=p, angle=-90)

# Add carrier outter box
fpga.add_fpga_carrier()

# Add some overall text
x, y = fpga.get_graph_corner(corner="ne")
cfg["pos"] = f"{x-1},{y-0.5}!"
cfg["shape"] = "plaintext"
cfg["fontsize"] = "20"
fpga.add_node_with_class("FPGA Carrier", **cfg)

# Output
fpga.draw("out.svg", prog="neato")
