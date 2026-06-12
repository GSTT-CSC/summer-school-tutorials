"""
HandOsteo care process diagram — generates an SVG swimlane flowchart.
Edit LANES and NODES/EDGES at the top to update the diagram.
"""
import svgwrite

# ── Layout constants ──────────────────────────────────────────────────────────
WIDTH = 900
LANE_HEIGHT = 100
LANE_LABEL_W = 140
NODE_W = 120
NODE_H = 50
DIAMOND_SIZE = 44      # half-width/height of decision diamonds
FONT = "Arial, sans-serif"

# ── Swimlane definitions (top → bottom) ──────────────────────────────────────
LANES = [
    {"id": "radiology",   "label": "Radiology",              "color": "#f0f4ff"},
    {"id": "pacs",        "label": "EHR / PACS",             "color": "#fff8e6"},
    {"id": "ai",          "label": "AI App\n(DeepC)",        "color": "#f0fff4"},
    {"id": "comms",       "label": "Patient / GP\nComms",    "color": "#fff0f0"},
]

# ── Nodes ─────────────────────────────────────────────────────────────────────
# x is fraction of drawable width (0–1); y_lane is LANES index; shape: box|diamond
NODES = [
    {"id": "xray",         "label": "AP Hand\nX-ray",                 "lane": 0, "x": 0.13, "shape": "box"},
    {"id": "pacs_store",   "label": "Image stored\nin PACS",          "lane": 1, "x": 0.33, "shape": "box"},
    {"id": "age_gate",     "label": "Age >50\n& AP view?",            "lane": 1, "x": 0.50, "shape": "diamond"},
    {"id": "deepc",        "label": "Run DeepC\nmodel",               "lane": 2, "x": 0.50, "shape": "box"},
    {"id": "result",       "label": "Result?",                        "lane": 2, "x": 0.67, "shape": "diamond"},
    {"id": "questionnaire","label": "Send questionnaire\nvia MyChart","lane": 3, "x": 0.60, "shape": "box"},
    {"id": "gp_letter",    "label": "Send letter to GP\n& patient via MyChart", "lane": 3, "x": 0.87, "shape": "box"},
]

# ── Edges ─────────────────────────────────────────────────────────────────────
EDGES = [
    {"from": "xray",          "to": "pacs_store",    "label": ""},
    {"from": "pacs_store",    "to": "age_gate",      "label": ""},
    {"from": "age_gate",      "to": "deepc",         "label": "Yes",  "exit": "bottom", "entry": "top"},
    {"from": "deepc",         "to": "result",        "label": ""},
    {"from": "result",        "to": "questionnaire", "label": "Osteopenia", "exit": "bottom", "entry": "top"},
    {"from": "result",        "to": "gp_letter",     "label": "Osteoporosis", "exit": "right"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def lane_y(lane_idx):
    """Top y-coordinate of a swimlane."""
    return lane_idx * LANE_HEIGHT


def node_cx(node):
    """Centre x of a node."""
    return LANE_LABEL_W + node["x"] * (WIDTH - LANE_LABEL_W)


def node_cy(node):
    """Centre y of a node."""
    return lane_y(node["lane"]) + LANE_HEIGHT // 2


def anchor(node, side):
    """Return (x, y) for a connection anchor on a given side."""
    cx, cy = node_cx(node), node_cy(node)
    if node["shape"] == "diamond":
        s = DIAMOND_SIZE
        return {
            "top":    (cx, cy - s),
            "bottom": (cx, cy + s),
            "left":   (cx - s, cy),
            "right":  (cx + s, cy),
        }[side]
    else:
        hw, hh = NODE_W / 2, NODE_H / 2
        return {
            "top":    (cx, cy - hh),
            "bottom": (cx, cy + hh),
            "left":   (cx - hw, cy),
            "right":  (cx + hw, cy),
        }[side]


def default_exit(src, dst):
    """Pick a sensible default exit side based on relative position."""
    if node_cx(dst) > node_cx(src) + 10:
        return "right"
    if node_cy(dst) > node_cy(src) + 10:
        return "bottom"
    return "right"


def default_entry(src, dst):
    if node_cx(dst) > node_cx(src) + 10:
        return "left"
    if node_cy(dst) > node_cy(src) + 10:
        return "top"
    return "left"


# ── Drawing ───────────────────────────────────────────────────────────────────

def draw_multiline(dwg, text, cx, cy, size=12, bold=False, color="black"):
    lines = text.split("\n")
    weight = "bold" if bold else "normal"
    line_h = size + 3
    total_h = line_h * len(lines)
    for i, line in enumerate(lines):
        y = cy - total_h / 2 + i * line_h + size
        dwg.add(dwg.text(line, insert=(cx, y), text_anchor="middle",
                         font_family=FONT, font_size=size,
                         font_weight=weight, fill=color))


def build_diagram():
    total_h = LANE_HEIGHT * len(LANES)
    dwg = svgwrite.Drawing(size=(WIDTH, total_h))

    node_map = {n["id"]: n for n in NODES}

    # Swimlane bands
    for i, lane in enumerate(LANES):
        y = lane_y(i)
        dwg.add(dwg.rect((0, y), (WIDTH, LANE_HEIGHT),
                         fill=lane["color"], stroke="#aaa", stroke_width=1))
        # Label box
        dwg.add(dwg.rect((0, y), (LANE_LABEL_W, LANE_HEIGHT),
                         fill="#dde", stroke="#aaa", stroke_width=1))
        lines = lane["label"].split("\n")
        for j, line in enumerate(lines):
            ly = y + LANE_HEIGHT / 2 + (j - (len(lines) - 1) / 2) * 16
            dwg.add(dwg.text(line, insert=(LANE_LABEL_W / 2, ly),
                             text_anchor="middle", font_family=FONT,
                             font_size=18, font_weight="bold", fill="#333"))

    # Nodes
    for node in NODES:
        cx, cy = node_cx(node), node_cy(node)
        if node["shape"] == "diamond":
            s = DIAMOND_SIZE
            pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
            dwg.add(dwg.polygon(pts, fill="white", stroke="#555", stroke_width=1.5))
        else:
            dwg.add(dwg.rect((cx - NODE_W / 2, cy - NODE_H / 2), (NODE_W, NODE_H),
                             rx=6, ry=6, fill="white", stroke="#555", stroke_width=1.5))
        draw_multiline(dwg, node["label"], cx, cy, size=11)

    # Edges
    arrow = dwg.marker(insert=(6, 3), size=(12, 6), orient="auto", id="arrow")
    arrow.add(dwg.path("M0,0 L0,6 L9,3 z", fill="#555"))
    dwg.defs.add(arrow)

    for edge in EDGES:
        src = node_map[edge["from"]]
        dst = node_map[edge["to"]]
        ex = edge.get("exit",  default_exit(src, dst))
        en = edge.get("entry", default_entry(src, dst))
        x1, y1 = anchor(src, ex)
        x2, y2 = anchor(dst, en)

        # Simple elbow: one midpoint
        if ex in ("left", "right"):
            mx, my = (x1 + x2) / 2, y1
            path = f"M{x1},{y1} L{mx},{my} L{mx},{y2} L{x2},{y2}"
        else:
            mx, my = x1, (y1 + y2) / 2
            path = f"M{x1},{y1} L{mx},{my} L{x2},{my} L{x2},{y2}"

        dwg.add(dwg.path(path, fill="none", stroke="#555", stroke_width=1.5,
                         marker_end="url(#arrow)"))

        if edge["label"]:
            lx = (x1 + x2) / 2
            ly = (y1 + y2) / 2 - 4
            dwg.add(dwg.text(edge["label"], insert=(lx, ly), text_anchor="middle",
                             font_family=FONT, font_size=14, fill="#333"))

    return dwg.tostring()


if __name__ == "__main__":
    svg = build_diagram()
    with open("care_process_diagram.svg", "w") as f:
        f.write(svg)
    print("Saved care_process_diagram.svg")
