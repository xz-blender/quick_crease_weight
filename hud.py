# SPDX-License-Identifier: GPL-2.0-or-later
"""Compact viewport cards with feathered rounded edges and measured text."""
from math import cos, pi, sin

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from .preferences import get_preferences

HINT_ROWS = (
    (("Shift", "吸附 0.1"), ("Ctrl", "设为 1"), ("Alt", "设为 0")),
    (("LMB / Enter", "确认"), ("RMB / Esc", "取消")),
)


def tint(color, opacity):
    return (*color[:3], color[3] * opacity)


def outline(x, y, width, height, radius, segments):
    radius = max(0.0, min(radius, width / 2, height / 2))
    corners = ((x + width - radius, y + radius, -pi / 2),
               (x + width - radius, y + height - radius, 0),
               (x + radius, y + height - radius, pi / 2),
               (x + radius, y + radius, pi))
    return [(cx + radius * cos(angle + step * pi / (2 * segments)),
             cy + radius * sin(angle + step * pi / (2 * segments)))
            for cx, cy, angle in corners for step in range(segments + 1)]


def rounded_rect(shader, x, y, width, height, radius, color):
    if width <= 0 or height <= 0 or color[3] <= 0:
        return
    # BLF can reset GPU blending between text and shape draws.
    gpu.state.blend_set("ALPHA")
    radius = max(0.0, min(radius, width / 2, height / 2))
    segments = max(4, min(24, int(radius * 0.8)))
    # Interpolate alpha across a one-pixel fringe, independent of UI scale.
    feather = min(0.65, width / 4, height / 4)
    inner = outline(x + feather, y + feather, width - 2 * feather, height - 2 * feather,
                    max(0.0, radius - feather), segments)
    outer = outline(x - feather, y - feather, width + 2 * feather, height + 2 * feather,
                    radius + feather, segments)
    count = len(inner)
    positions = [(x + width / 2, y + height / 2), *inner, *outer]
    colors = [color] * (count + 1) + [(*color[:3], 0.0)] * count
    triangles = []
    for index in range(count):
        a, b = 1 + index, 1 + (index + 1) % count
        triangles.extend(((0, a, b), (a, a + count, b + count), (a, b + count, b)))
    batch = batch_for_shader(shader, "TRIS", {"pos": positions, "color": colors}, indices=triangles)
    shader.bind()
    batch.draw(shader)


def text_width(text, size):
    blf.size(0, size)
    return blf.dimensions(0, text)[0]


def text_at(text, x, y, size, color):
    blf.size(0, size)
    blf.color(0, *color)
    blf.position(0, x, y, 0)
    blf.draw(0, text)


def hint_width(key, label, size, scale):
    return text_width(key, size) + text_width(label, size) + 23 * scale


def card_layout(operator, prefs, scale):
    size = prefs.hud_font_size * scale
    small = max(12.0, min(15.0, prefs.hud_font_size * 0.34)) * scale
    title_size = 14 * scale
    domain = "顶点" if operator._edit.domain == "POINT" else "边"
    badge = f"{domain}  ·  {operator._edit.count}"
    pad = 20 * scale
    widths = [text_width(operator.display_name, title_size) + text_width(badge, small) + 62 * scale,
              text_width("1.00", size) + text_width("左右拖动", small) + 35 * scale]
    if prefs.hud_show_help:
        widths.extend(sum(hint_width(key, label, small, scale) for key, label in row)
                      + (len(row) - 1) * 14 * scale for row in HINT_ROWS)
    width = max(300 * scale, max(widths) + 2 * pad)
    header = 24 * scale
    value_row = size + 20 * scale
    bar_row = 20 * scale if prefs.hud_show_bar else 0
    footer = 82 * scale if prefs.hud_show_help else 0
    return {"width": width, "height": 2 * pad + header + value_row + bar_row + footer,
            "scale": scale, "size": size, "small": small, "title_size": title_size,
            "pad": pad, "header": header, "value_row": value_row, "badge": badge}


def draw_hints(shader, x, top, width, size, scale, color):
    for row in HINT_ROWS:
        total = sum(hint_width(key, label, size, scale) for key, label in row)
        gap = (width - total) / max(1, len(row) - 1)
        cursor = x
        for key, label in row:
            key_width = text_width(key, size) + 16 * scale
            rounded_rect(shader, cursor, top - 25 * scale, key_width, 25 * scale, 5 * scale,
                         tint(color, 0.075))
            text_at(key, cursor + 8 * scale, top - 18 * scale, size, tint(color, 0.95))
            text_at(label, cursor + key_width + 7 * scale, top - 18 * scale, size, tint(color, 0.66))
            cursor += hint_width(key, label, size, scale) + gap
        top -= 34 * scale


def viewport_bounds(area, region):
    """Exclude overlapping toolbars and sidebars from the card's safe area."""
    left, bottom, right, top = 0, 0, region.width, region.height
    for other in area.regions:
        if other.type not in {"HEADER", "TOOL_HEADER", "TOOLS", "UI"}:
            continue
        x0, y0 = other.x - region.x, other.y - region.y
        x1, y1 = x0 + other.width, y0 + other.height
        if other.width <= 1 or other.height <= 1 or x1 <= 0 or y1 <= 0:
            continue
        if x0 >= region.width or y0 >= region.height:
            continue
        if other.type in {"HEADER", "TOOL_HEADER"}:
            if y0 > region.height / 2:
                top = min(top, y0)
            else:
                bottom = max(bottom, y1)
        elif x0 < region.width / 2:
            left = max(left, x1)
        else:
            right = min(right, x0)
    return left, bottom, max(1, right - left), max(1, top - bottom)


def draw(operator):
    context = bpy.context
    if context.area != operator._area or context.region != operator._region:
        return
    prefs = get_preferences(context)
    if prefs is None or not prefs.show_hud:
        return
    region = context.region
    view_x, view_y, view_width, view_height = viewport_bounds(context.area, region)
    ui_scale = context.preferences.system.ui_scale
    layout = card_layout(operator, prefs, ui_scale)
    margin = min(8 * ui_scale, view_width / 8, view_height / 8)
    fit = min(1.0, (view_width - 2 * margin) / layout["width"],
              (view_height - 2 * margin) / layout["height"])
    if fit <= 0:
        return
    if fit < 1:
        layout = card_layout(operator, prefs, ui_scale * fit)
    width, height, scale = layout["width"], layout["height"], layout["scale"]
    pad, small, size = layout["pad"], layout["small"], layout["size"]
    offset_x, offset_y = prefs.hud_offset_x * ui_scale, prefs.hud_offset_y * ui_scale
    if prefs.hud_anchor == "CURSOR":
        x, y = operator._mouse_region[0] + 24 * ui_scale + offset_x, operator._mouse_region[1] + offset_y
    else:
        x = view_x + (view_width - width) / 2 + offset_x
        y = view_y + view_height - height - offset_y if prefs.hud_anchor == "TOP" else view_y + offset_y
    x = max(view_x + margin, min(x, view_x + view_width - width - margin))
    y = max(view_y + margin, min(y, view_y + view_height - height - margin))
    radius = prefs.hud_corner_radius * scale
    color, accent = tuple(prefs.hud_text_color), tuple(prefs.hud_value_color)
    blend = gpu.state.blend_get()
    try:
        gpu.state.blend_set("ALPHA")
        shader = gpu.shader.from_builtin("SMOOTH_COLOR")
        if prefs.hud_background:
            background = tuple(prefs.hud_background_color)
            if prefs.hud_panel_shadow:
                for spread, opacity in ((7, 0.045), (4, 0.07), (1, 0.12)):
                    edge = spread * scale
                    rounded_rect(shader, x - edge, y - edge - 3 * scale,
                                 width + 2 * edge, height + 2 * edge, radius + edge,
                                 (0.0, 0.0, 0.0, opacity * background[3]))
            rounded_rect(shader, x, y, width, height, radius, background)
            # Subtle top highlight without a second translucent card compositing over the first.
            rounded_rect(shader, x + radius, y + height - scale, max(0, width - 2 * radius),
                         scale, scale / 2, tint(color, 0.1 * background[3]))
        if prefs.hud_shadow:
            blf.enable(0, blf.SHADOW)
            blf.shadow(0, 3, 0.0, 0.0, 0.0, 0.6)
            blf.shadow_offset(0, 1, -1)
        else:
            blf.disable(0, blf.SHADOW)
        left, right = x + pad, x + width - pad
        top = y + height - pad
        rounded_rect(shader, left, top - 16 * scale, 6 * scale, 6 * scale, 3 * scale, accent)
        text_at(operator.display_name, left + 14 * scale, top - 18 * scale,
                layout["title_size"], color)
        badge_width = text_width(layout["badge"], small) + 18 * scale
        rounded_rect(shader, right - badge_width, top - 24 * scale, badge_width, 24 * scale,
                     12 * scale, tint(accent, 0.1))
        text_at(layout["badge"], right - badge_width + 9 * scale, top - 17 * scale,
                small, tint(accent, 0.9))
        top -= layout["header"]
        baseline = top - size - 6 * scale
        text_at(f"{operator.value:.2f}", left, baseline, size, accent)
        drag = "左右拖动"
        text_at(drag, right - text_width(drag, small), baseline + 3 * scale, small, tint(color, 0.5))
        top -= layout["value_row"]
        if prefs.hud_show_bar:
            bar_y, bar_height = top - 6 * scale, 6 * scale
            rounded_rect(shader, left, bar_y, right - left, bar_height, bar_height / 2, tint(color, 0.1))
            rounded_rect(shader, left, bar_y, (right - left) * operator.value,
                         bar_height, bar_height / 2, accent)
            top -= 20 * scale
        if prefs.hud_show_help:
            rounded_rect(shader, left, top - scale, right - left, scale, 0, tint(color, 0.075))
            draw_hints(shader, left, top - 14 * scale, right - left, small, scale, color)
    finally:
        blf.disable(0, blf.SHADOW)
        gpu.state.blend_set(blend)
