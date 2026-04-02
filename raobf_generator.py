#!/usr/bin/env python3
"""
RAOBF wheel SVG generator with curved arc labels.
Outputs:
  - raobf_base.svg
  - raobf_rotor.svg
  - raobf_composite.svg
"""

import math
from dataclasses import dataclass

PAGE_W = 220.0
PAGE_H = 220.0
CX = PAGE_W / 2.0
CY = PAGE_H / 2.0

BASE_RADIUS = 89.0
ROTOR_RADIUS = 88.0
PIVOT_RADIUS = 2.25

SHIP_R_OUTER = 79.0
SHIP_LABEL_R = 83.0
BASIS_TEXT_R = 82.0

DIST_R_OUTER = 78.0
DIST_LABEL_R = 73.0
DIST_TEXT_R = 73.0

OPT_R_OUTER = 61.0
OPT_LABEL_R = 65.0
OPT_TEXT_R = 64.0

AOB_R_OUTER = 60.0
AOB_LABEL_R = 55.0
AOB_TEXT_R = 54.0

TICK_LENGTHS = {"major": 2.5, "thick": 1.25, "thin": 0.625}
STROKE_WIDTHS = {"major": 0.35, "thick": 0.35, "thin": 0.18}
SHIP_BORDER_R = SHIP_R_OUTER
DIST_BORDER_R = DIST_R_OUTER
OPT_BORDER_R = OPT_R_OUTER
AOB_OUTER_BORDER_R = AOB_R_OUTER
AOB_INNER_BORDER_R = AOB_R_OUTER - 8
AOB_CROSSHAIR_HORIZONTAL_TICKS_PER_DIRECTION = 11
AOB_CROSSHAIR_VERTICAL_TICKS_PER_DIRECTION = 10
AOB_CROSSHAIR_EXTENT_RATIO = 0.85
AOB_CROSSHAIR_LINE_WIDTH = 0.20
AOB_CROSSHAIR_MINOR_TICK_LEN = 1.2
AOB_CROSSHAIR_MAJOR_TICK_LEN = 2.2
AOB_CROSSHAIR_MINOR_TICK_WIDTH = 0.18
AOB_CROSSHAIR_MAJOR_TICK_WIDTH = 0.30
NUMBER_FONT_FAMILY = "Helvetica, Arial, sans-serif"
TEXT_FONT_FAMILY = "Futura, Avenir Next, Helvetica, sans-serif"
NUMBER_LABEL_FONT_SIZE = 4.0
TEXT_LABEL_FONT_SIZE = 4.5
MARKER_LABEL_FONT_SIZE = 3.4
MARKER_LABEL_CLOCKWISE_OFFSET_DEG = 1.0
SHIP_ZERO_MARKER_COLOR = "#1f5fbf"
SHIP_ZERO_MARKER_WIDTH = 0.75
SHIP_ZERO_MARKER_COVER_WIDTH = 1.15
SHIP_ZERO_TOP_MARKER_LENGTH = 4.0
SHIP_BLUE_LABEL_TEXT = "6x"
SHIP_BLUE_LABEL_R = 86.0
SHIP_BLUE_LABEL_SPAN_DEG = 12.0
SHIP_GREEN_MARKER_COLOR = "#1f8a3b"
SHIP_GREEN_MARKER_WIDTH = 0.75
SHIP_GREEN_MARKER_CLOCKWISE_DEG = 109.0
SHIP_GREEN_LABEL_TEXT = "1.5x"
SHIP_GREEN_LABEL_R = 86.0
SHIP_GREEN_LABEL_SPAN_DEG = 12.0
AOB_MARKER_COLOR = "#c62828"
AOB_MARKER_WIDTH = 0.75
AOB_MARKER_CLOCKWISE_DEG = 13.0
AOB_LABEL_TEXT = "kts"
AOB_MARKER_LABEL_R = 53.0
AOB_LABEL_SPAN_DEG = 14.0
MARKER_ARROW_LENGTH = 2.4
MARKER_ARROW_WIDTH = 1.9

K = math.pi / math.log(10.0)
OPTICAL_OFFSET = math.radians(316.0)
AOB_MIN_DEG = 5.0
AOB_MAX_WHEEL_RAD = math.radians(190.0)
SHIP_ROTATE_OFFSET = math.pi


@dataclass(frozen=True)
class TickSpec:
    value: float
    theta_rad: float
    kind: str
    label: str = ""


def frange(start, stop, step):
    vals = []
    n = 0
    eps = abs(step) / 1000.0
    while True:
        x = start + n * step
        if x > stop + eps:
            break
        vals.append(round(x, 10))
        n += 1
    return vals


def fmt_num(x):
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.10g}"


def wheel_to_svg_angle(theta):
    return math.pi / 2.0 - theta


def polar(cx, cy, r, ang):
    x = cx + r * math.cos(ang)
    y = cy - r * math.sin(ang)
    return x, y


def svg_line(x1, y1, x2, y2, w, stroke="black"):
    return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{stroke}" stroke-width="{w:.3f}" />'


def svg_circle(cx, cy, r):
    return f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" stroke="black" stroke-width="0.20" fill="none" />'


def svg_arrowhead(tip_x, tip_y, from_x, from_y, fill, length=MARKER_ARROW_LENGTH, width=MARKER_ARROW_WIDTH):
    dx = tip_x - from_x
    dy = tip_y - from_y
    mag = math.hypot(dx, dy)
    if mag == 0:
        return ""
    ux = dx / mag
    uy = dy / mag
    bx = tip_x - ux * length
    by = tip_y - uy * length
    px = -uy * (width / 2.0)
    py = ux * (width / 2.0)
    return (
        f'<polygon points="{tip_x:.3f},{tip_y:.3f} {bx + px:.3f},{by + py:.3f} {bx - px:.3f},{by - py:.3f}" '
        f'fill="{fill}" stroke="none" />'
    )


def svg_text(
    x,
    y,
    text,
    font_size=NUMBER_LABEL_FONT_SIZE,
    rotation=None,
    font_family=NUMBER_FONT_FAMILY,
):
    transform = ""
    if rotation is not None:
        transform = f' transform="rotate({math.degrees(rotation):.3f} {x:.3f} {y:.3f})"'
    return (
        f'<text x="{x:.3f}" y="{y:.3f}" font-size="{font_size:.3f}" font-family="{font_family}" '
        f'text-anchor="middle" dominant-baseline="middle"{transform}>{text}</text>'
    )


def svg_path(path_id, d):
    return f'<path id="{path_id}" d="{d}" fill="none" stroke="none" />'


def svg_text_on_arc(
    path_id,
    text,
    font_size=TEXT_LABEL_FONT_SIZE,
    font_family=TEXT_FONT_FAMILY,
    fill="black",
    start_offset="50%",
    text_anchor="middle",
):
    return (
        f'<text font-size="{font_size:.3f}" font-family="{font_family}" fill="{fill}">'
        f'<textPath href="#{path_id}" xlink:href="#{path_id}" startOffset="{start_offset}" text-anchor="{text_anchor}">'
        f"{text}</textPath>"
        f"</text>"
    )


def label_rotation(theta_rad):
    return theta_rad


def arc_path_d(cx, cy, radius, start_wheel_deg, end_wheel_deg):
    start_theta = math.radians(start_wheel_deg)
    end_theta = math.radians(end_wheel_deg)
    start_svg = wheel_to_svg_angle(start_theta)
    end_svg = wheel_to_svg_angle(end_theta)
    x1, y1 = polar(cx, cy, radius, start_svg)
    x2, y2 = polar(cx, cy, radius, end_svg)
    delta = (end_wheel_deg - start_wheel_deg) % 360
    large_arc = 1 if delta > 180 else 0
    sweep = 1
    return (
        f"M {x1:.3f} {y1:.3f} "
        f"A {radius:.3f} {radius:.3f} 0 {large_arc} {sweep} {x2:.3f} {y2:.3f}"
    )


def theta_ship(x):
    return ((K * math.log(x / 10.0)) + SHIP_ROTATE_OFFSET) % (2.0 * math.pi)


def theta_distance(d):
    return (K * math.log(d / 10.0)) % (2.0 * math.pi)


def theta_optical(l):
    return (OPTICAL_OFFSET + K * math.log(40.0 / l)) % (2.0 * math.pi)


def theta_aob(aob_deg):
    a = math.radians(aob_deg)
    denom = math.log(1.0 / math.sin(math.radians(AOB_MIN_DEG)))
    return AOB_MAX_WHEEL_RAD * math.log(1.0 / math.sin(a)) / denom


def draw_scale(
    elements,
    ticks,
    r_outer,
    label_radius=None,
    font_size=NUMBER_LABEL_FONT_SIZE,
    tick_direction="inward",
    tick_direction_fn=None,
):
    for tick in ticks:
        current_direction = (
            tick_direction_fn(tick) if tick_direction_fn is not None else tick_direction
        )
        tick_sign = -1.0 if current_direction == "inward" else 1.0
        svg_ang = wheel_to_svg_angle(tick.theta_rad)
        x1, y1 = polar(CX, CY, r_outer, svg_ang)
        x2, y2 = polar(CX, CY, r_outer + tick_sign * TICK_LENGTHS[tick.kind], svg_ang)
        elements.append(svg_line(x1, y1, x2, y2, STROKE_WIDTHS[tick.kind]))
        if tick.label and label_radius is not None:
            lx, ly = polar(CX, CY, label_radius, svg_ang)
            rot = label_rotation(tick.theta_rad)
            elements.append(
                svg_text(lx, ly, tick.label, font_size=font_size, rotation=rot)
            )


def add_tick(ticks, value, theta_fn, kind, label=""):
    value = round(float(value), 10)
    theta = theta_fn(value)
    old = ticks.get(value)
    priority = {"thin": 0, "thick": 1, "major": 2}
    new = TickSpec(value, theta, kind, label)
    if old is None or priority[kind] > priority[old.kind] or label:
        ticks[value] = new


def build_ship_ticks():
    labels = {
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        20,
        25,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        110,
        120,
        130,
        140,
        150,
        200,
        250,
        300,
    }
    ticks = {}
    for v in labels:
        add_tick(ticks, v, theta_ship, "major", fmt_num(v))
    for v in frange(5.0, 10.0, 0.1):
        if v in labels:
            continue
        if abs((v * 10) % 5) < 1e-9:
            add_tick(ticks, v, theta_ship, "thick")
        else:
            add_tick(ticks, v, theta_ship, "thin")
    for v in frange(10.0, 15.0, 0.5):
        if v not in labels:
            add_tick(ticks, v, theta_ship, "thick")
    for v in frange(15.0, 30.0, 1.0):
        if v not in labels:
            add_tick(ticks, v, theta_ship, "thick")
    for v in frange(30.0, 50.0, 1.0):
        if v in labels:
            continue
        if int(round(v)) % 2 == 0:
            add_tick(ticks, v, theta_ship, "thick")
        else:
            add_tick(ticks, v, theta_ship, "thin")
    for v in frange(50.0, 100.0, 1.0):
        if v in labels:
            continue
        if int(round(v)) % 5 == 0:
            add_tick(ticks, v, theta_ship, "thick")
        else:
            add_tick(ticks, v, theta_ship, "thin")
    for v in frange(100.0, 150.0, 5.0):
        if v not in labels:
            add_tick(ticks, v, theta_ship, "thick")
    for v in frange(150.0, 300.0, 10.0):
        if v not in labels:
            add_tick(ticks, v, theta_ship, "thick")
    return [ticks[k] for k in sorted(ticks)]


def build_distance_ticks():
    labels = {
        2,
        2.5,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        20,
        25,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
    }
    ticks = {}
    for v in labels:
        add_tick(ticks, v, theta_distance, "major", fmt_num(v))
    for v in frange(2.0, 3.0, 0.2):
        if v not in labels:
            add_tick(ticks, v, theta_distance, "thin")
    for v in frange(3.0, 5.0, 0.1):
        if v in labels:
            continue
        if abs((v * 10) % 2) < 1e-9:
            add_tick(ticks, v, theta_distance, "thick")
        else:
            add_tick(ticks, v, theta_distance, "thin")
    for v in frange(5.0, 10.0, 0.1):
        if v in labels:
            continue
        if abs((v * 10) % 5) < 1e-9:
            add_tick(ticks, v, theta_distance, "thick")
        else:
            add_tick(ticks, v, theta_distance, "thin")
    for v in frange(10.0, 15.0, 0.5):
        if v not in labels:
            add_tick(ticks, v, theta_distance, "thick")
    for v in frange(15.0, 30.0, 1.0):
        if v not in labels:
            add_tick(ticks, v, theta_distance, "thick")
    for v in frange(30.0, 50.0, 2.0):
        if v not in labels:
            add_tick(ticks, v, theta_distance, "thick")
    for v in frange(50.0, 100.0, 1.0):
        if v in labels:
            continue
        if int(round(v)) % 5 == 0:
            add_tick(ticks, v, theta_distance, "thick")
        else:
            add_tick(ticks, v, theta_distance, "thin")
    return [ticks[k] for k in sorted(ticks)]


def build_optical_ticks():
    labels = {
        0.5,
        1,
        1.5,
        2,
        2.5,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        20,
        25,
        30,
        40,
    }
    ticks = {}
    for v in labels:
        add_tick(ticks, v, theta_optical, "major", fmt_num(v))
    for v in frange(0.5, 1.5, 0.05):
        if v in labels:
            continue
        if abs((v * 100) % 10) < 1e-9:
            add_tick(ticks, v, theta_optical, "thick")
        else:
            add_tick(ticks, v, theta_optical, "thin")
    for v in frange(1.5, 3.0, 0.1):
        if v not in labels:
            add_tick(ticks, v, theta_optical, "thick")
    for v in frange(3.0, 5.0, 0.2):
        if v not in labels:
            add_tick(ticks, v, theta_optical, "thick")
    for v in frange(5.0, 15.0, 0.5):
        if v not in labels:
            add_tick(ticks, v, theta_optical, "thick")
    for v in frange(15.0, 30.0, 1.0):
        if v not in labels:
            add_tick(ticks, v, theta_optical, "thick")
    for v in frange(30.0, 40.0, 2.0):
        if v not in labels:
            add_tick(ticks, v, theta_optical, "thick")
    return [ticks[k] for k in sorted(ticks)]


def build_aob_ticks():
    labels = {5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 90}
    ticks = {}
    for v in labels:
        add_tick(ticks, v, theta_aob, "major", fmt_num(v))
    for v in frange(5.0, 50.0, 1.0):
        if v not in labels:
            add_tick(ticks, v, theta_aob, "thick")
    for v in frange(50.0, 60.0, 1.0):
        if v in labels:
            continue
        if abs(v - 55.0) < 1e-9:
            add_tick(ticks, v, theta_aob, "thick")
        else:
            add_tick(ticks, v, theta_aob, "thin")
    for v in [65.0, 80.0]:
        if v not in labels:
            add_tick(ticks, v, theta_aob, "thick")
    return [ticks[k] for k in sorted(ticks)]


def build_base():
    defs = []
    elems = []
    elems.append(svg_circle(CX, CY, BASE_RADIUS))
    elems.append(svg_circle(CX, CY, PIVOT_RADIUS))
    elems.append(svg_circle(CX, CY, SHIP_BORDER_R))
    elems.append(svg_circle(CX, CY, AOB_OUTER_BORDER_R))
    elems.append(svg_circle(CX, CY, AOB_INNER_BORDER_R))
    elems.append(
        svg_line(
            CX - AOB_INNER_BORDER_R,
            CY,
            CX + AOB_INNER_BORDER_R,
            CY,
            AOB_CROSSHAIR_LINE_WIDTH,
        )
    )
    elems.append(
        svg_line(
            CX,
            CY - AOB_INNER_BORDER_R,
            CX,
            CY + AOB_INNER_BORDER_R,
            AOB_CROSSHAIR_LINE_WIDTH,
        )
    )
    aob_crosshair_extent = AOB_INNER_BORDER_R * AOB_CROSSHAIR_EXTENT_RATIO
    aob_crosshair_horizontal_step = (
        aob_crosshair_extent / AOB_CROSSHAIR_HORIZONTAL_TICKS_PER_DIRECTION
    )
    aob_crosshair_vertical_step = (
        aob_crosshair_extent / AOB_CROSSHAIR_VERTICAL_TICKS_PER_DIRECTION
    )
    for i in range(1, AOB_CROSSHAIR_HORIZONTAL_TICKS_PER_DIRECTION + 1):
        tick_offset = i * aob_crosshair_horizontal_step
        is_major = (i % 5) == 0
        tick_len = (
            AOB_CROSSHAIR_MAJOR_TICK_LEN if is_major else AOB_CROSSHAIR_MINOR_TICK_LEN
        )
        tick_width = (
            AOB_CROSSHAIR_MAJOR_TICK_WIDTH
            if is_major
            else AOB_CROSSHAIR_MINOR_TICK_WIDTH
        )
        elems.append(
            svg_line(CX + tick_offset, CY - tick_len, CX + tick_offset, CY + tick_len, tick_width)
        )
        elems.append(
            svg_line(CX - tick_offset, CY - tick_len, CX - tick_offset, CY + tick_len, tick_width)
        )
    for i in range(1, AOB_CROSSHAIR_VERTICAL_TICKS_PER_DIRECTION + 1):
        tick_offset = i * aob_crosshair_vertical_step
        is_major = (i % 5) == 0
        tick_len = (
            AOB_CROSSHAIR_MAJOR_TICK_LEN if is_major else AOB_CROSSHAIR_MINOR_TICK_LEN
        )
        tick_width = (
            AOB_CROSSHAIR_MAJOR_TICK_WIDTH
            if is_major
            else AOB_CROSSHAIR_MINOR_TICK_WIDTH
        )
        elems.append(
            svg_line(CX - tick_len, CY + tick_offset, CX + tick_len, CY + tick_offset, tick_width)
        )
        elems.append(
            svg_line(CX - tick_len, CY - tick_offset, CX + tick_len, CY - tick_offset, tick_width)
        )
    draw_scale(
        elems,
        build_ship_ticks(),
        SHIP_R_OUTER,
        SHIP_LABEL_R,
        NUMBER_LABEL_FONT_SIZE,
        tick_direction="outward",
    )
    ship_zero_svg_ang = wheel_to_svg_angle(theta_ship(100.0))
    x1, y1 = polar(CX, CY, SHIP_R_OUTER, ship_zero_svg_ang)
    x2, y2 = polar(CX, CY, SHIP_R_OUTER + TICK_LENGTHS["major"], ship_zero_svg_ang)
    elems.append(
        svg_line(x1, y1, x2, y2, SHIP_ZERO_MARKER_COVER_WIDTH, "white")
    )
    elems.append(
        svg_line(x1, y1, x2, y2, SHIP_ZERO_MARKER_WIDTH, SHIP_ZERO_MARKER_COLOR)
    )
    elems.append(svg_arrowhead(x1, y1, x2, y2, SHIP_ZERO_MARKER_COLOR))
    x3, y3 = polar(CX, CY, BASE_RADIUS, ship_zero_svg_ang)
    x4, y4 = polar(CX, CY, BASE_RADIUS - SHIP_ZERO_TOP_MARKER_LENGTH, ship_zero_svg_ang)
    elems.append(
        svg_line(x3, y3, x4, y4, SHIP_ZERO_MARKER_COVER_WIDTH, "white")
    )
    elems.append(
        svg_line(x3, y3, x4, y4, SHIP_ZERO_MARKER_WIDTH, SHIP_ZERO_MARKER_COLOR)
    )
    ship_zero_wheel_deg = math.degrees(theta_ship(100.0)) % 360.0
    defs.append(
        svg_path(
            "ship_blue_label_arc",
            arc_path_d(
                CX,
                CY,
                SHIP_BLUE_LABEL_R,
                ship_zero_wheel_deg + MARKER_LABEL_CLOCKWISE_OFFSET_DEG,
                ship_zero_wheel_deg
                + MARKER_LABEL_CLOCKWISE_OFFSET_DEG
                + SHIP_BLUE_LABEL_SPAN_DEG,
            ),
        )
    )
    elems.append(
        svg_text_on_arc(
            "ship_blue_label_arc",
            SHIP_BLUE_LABEL_TEXT,
            MARKER_LABEL_FONT_SIZE,
            NUMBER_FONT_FAMILY,
            SHIP_ZERO_MARKER_COLOR,
            "0%",
            "start",
        )
    )
    ship_green_svg_ang = ship_zero_svg_ang - math.radians(SHIP_GREEN_MARKER_CLOCKWISE_DEG)
    x5, y5 = polar(CX, CY, BASE_RADIUS, ship_green_svg_ang)
    x6, y6 = polar(CX, CY, SHIP_BORDER_R, ship_green_svg_ang)
    elems.append(
        svg_line(x5, y5, x6, y6, SHIP_GREEN_MARKER_WIDTH, SHIP_GREEN_MARKER_COLOR)
    )
    elems.append(svg_arrowhead(x6, y6, x5, y5, SHIP_GREEN_MARKER_COLOR))
    ship_green_wheel_deg = (ship_zero_wheel_deg + SHIP_GREEN_MARKER_CLOCKWISE_DEG) % 360.0
    defs.append(
        svg_path(
            "ship_green_label_arc",
            arc_path_d(
                CX,
                CY,
                SHIP_GREEN_LABEL_R,
                ship_green_wheel_deg + MARKER_LABEL_CLOCKWISE_OFFSET_DEG,
                ship_green_wheel_deg
                + MARKER_LABEL_CLOCKWISE_OFFSET_DEG
                + SHIP_GREEN_LABEL_SPAN_DEG,
            ),
        )
    )
    elems.append(
        svg_text_on_arc(
            "ship_green_label_arc",
            SHIP_GREEN_LABEL_TEXT,
            MARKER_LABEL_FONT_SIZE,
            NUMBER_FONT_FAMILY,
            SHIP_GREEN_MARKER_COLOR,
            "0%",
            "start",
        )
    )
    draw_scale(
        elems, build_aob_ticks(), AOB_R_OUTER, AOB_LABEL_R, NUMBER_LABEL_FONT_SIZE
    )
    aob_marker_svg_ang = wheel_to_svg_angle(math.radians(AOB_MARKER_CLOCKWISE_DEG))
    x7, y7 = polar(CX, CY, AOB_OUTER_BORDER_R, aob_marker_svg_ang)
    x8, y8 = polar(CX, CY, AOB_INNER_BORDER_R, aob_marker_svg_ang)
    elems.append(svg_line(x7, y7, x8, y8, AOB_MARKER_WIDTH, AOB_MARKER_COLOR))
    elems.append(svg_arrowhead(x7, y7, x8, y8, AOB_MARKER_COLOR))
    defs.append(
        svg_path(
            "aob_marker_label_arc",
            arc_path_d(
                CX,
                CY,
                AOB_MARKER_LABEL_R,
                AOB_MARKER_CLOCKWISE_DEG + MARKER_LABEL_CLOCKWISE_OFFSET_DEG,
                AOB_MARKER_CLOCKWISE_DEG
                + MARKER_LABEL_CLOCKWISE_OFFSET_DEG
                + AOB_LABEL_SPAN_DEG,
            ),
        )
    )
    elems.append(
        svg_text_on_arc(
            "aob_marker_label_arc",
            AOB_LABEL_TEXT,
            MARKER_LABEL_FONT_SIZE,
            NUMBER_FONT_FAMILY,
            AOB_MARKER_COLOR,
            "0%",
            "start",
        )
    )
    defs.append(svg_path("basis_arc", arc_path_d(CX, CY, BASIS_TEXT_R, 55.0, 155.0)))
    elems.append(svg_text_on_arc("basis_arc", "Basis in Meter", TEXT_LABEL_FONT_SIZE))
    defs.append(svg_path("aob_arc", arc_path_d(CX, CY, AOB_TEXT_R, 277.0, 367.0)))
    elems.append(svg_text_on_arc("aob_arc", "Zielkurswinkel", TEXT_LABEL_FONT_SIZE))
    return defs, elems


def build_rotor():
    defs = []
    elems = []
    elems.append(svg_circle(CX, CY, ROTOR_RADIUS))
    elems.append(svg_circle(CX, CY, PIVOT_RADIUS))
    elems.append(svg_circle(CX, CY, DIST_BORDER_R))
    elems.append(svg_circle(CX, CY, OPT_BORDER_R))
    draw_scale(
        elems,
        build_distance_ticks(),
        DIST_R_OUTER,
        DIST_LABEL_R,
        NUMBER_LABEL_FONT_SIZE,
    )
    draw_scale(
        elems,
        build_optical_ticks(),
        OPT_R_OUTER,
        OPT_LABEL_R,
        NUMBER_LABEL_FONT_SIZE,
        tick_direction="outward",
    )
    defs.append(svg_path("dist_arc", arc_path_d(CX, CY, DIST_TEXT_R, 158.0, 258.0)))
    elems.append(
        svg_text_on_arc("dist_arc", "Entfernung in Hundertmeter", TEXT_LABEL_FONT_SIZE)
    )
    defs.append(svg_path("opt_arc", arc_path_d(CX, CY, OPT_TEXT_R, 247.0, 297.0)))
    elems.append(svg_text_on_arc("opt_arc", "Optische Länge", TEXT_LABEL_FONT_SIZE))
    return defs, elems


def write_svg(name, defs, elements):
    defs_block = ""
    if defs:
        defs_block = "<defs>" + "".join(defs) + "</defs>"
    content = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'     xmlns:xlink="http://www.w3.org/1999/xlink"\n'
        f'     width="{PAGE_W}mm"\n'
        f'     height="{PAGE_H}mm"\n'
        f'     viewBox="0 0 {PAGE_W} {PAGE_H}">\n'
        f"  {defs_block}\n"
        f"  <g>\n"
        f"    {''.join(elements)}\n"
        f"  </g>\n"
        f"</svg>\n"
    )
    with open(name, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    base_defs, base_elems = build_base()
    rotor_defs, rotor_elems = build_rotor()
    write_svg("raobf_base.svg", base_defs, base_elems)
    write_svg("raobf_rotor.svg", rotor_defs, rotor_elems)
    write_svg("raobf_composite.svg", base_defs + rotor_defs, base_elems + rotor_elems)
    print("Generated raobf_base.svg, raobf_rotor.svg, and raobf_composite.svg")


if __name__ == "__main__":
    main()
