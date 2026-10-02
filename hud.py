# SPDX-License-Identifier: GPL-2.0-or-later
import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from .preferences import get_preferences

HELP = "左键 / Enter 确认    Esc / 右键 还原"
MODIFIERS = "Shift 吸附 0.1    Ctrl = 1    Alt = 0"


def rectangle(shader, x, y, width, height, color):
    batch = batch_for_shader(shader, "TRIS", {"pos": (
        (x, y), (x + width, y), (x + width, y + height), (x, y + height),
    )}, indices=((0, 1, 2), (0, 2, 3)))
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def draw(operator):
    context = bpy.context
    if context.area != operator._area or context.region != operator._region:
        return
    prefs = get_preferences(context)
    if prefs is None or not prefs.show_hud:
        return
    region = context.region
    scale = context.preferences.system.ui_scale
    size = prefs.hud_font_size * scale
    small = max(12 * scale, size * 0.46)
    padding = 16 * scale
    gap = 9 * scale
    domain = "顶点" if operator._edit.domain == "POINT" else "边"
    title = f"{domain} · {operator.display_name}   /   {operator._edit.count} 个元素"
    lines = [(title, small, prefs.hud_text_color),
             (f"{operator.value:.2f}", size, prefs.hud_value_color)]
    if prefs.hud_show_help:
        lines.extend(((HELP, small, prefs.hud_text_color), (MODIFIERS, small, prefs.hud_text_color)))
    widths = []
    for text, font_size, _color in lines:
        blf.size(0, font_size)
        widths.append(blf.dimensions(0, text)[0])
    width = max(widths) + padding * 2
    bar_height = 5 * scale
    height = padding * 2 + sum(font_size + gap for _, font_size, _ in lines) - gap
    if prefs.hud_show_bar:
        height += bar_height + gap
    offset_x, offset_y = prefs.hud_offset_x * scale, prefs.hud_offset_y * scale
    if prefs.hud_anchor == "CURSOR":
        x = operator._mouse_region[0] + 24 * scale + offset_x
        y = operator._mouse_region[1] + offset_y
    else:
        x = (region.width - width) / 2 + offset_x
        y = region.height - height - offset_y if prefs.hud_anchor == "TOP" else offset_y
    x = max(8 * scale, min(x, region.width - width - 8 * scale))
    y = max(8 * scale, min(y, region.height - height - 8 * scale))
    blend = gpu.state.blend_get()
    try:
        gpu.state.blend_set("ALPHA")
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        if prefs.hud_background:
            rectangle(shader, x, y, width, height, prefs.hud_background_color)
        if prefs.hud_show_bar:
            rectangle(shader, x + padding, y + padding, width - padding * 2, bar_height, (1, 1, 1, 0.12))
            if operator.value > 0:
                rectangle(shader, x + padding, y + padding,
                          (width - padding * 2) * operator.value, bar_height, prefs.hud_value_color)
        if prefs.hud_shadow:
            blf.enable(0, blf.SHADOW)
            blf.shadow(0, 3, 0.0, 0.0, 0.0, 0.6)
            blf.shadow_offset(0, 1, -1)
        else:
            blf.disable(0, blf.SHADOW)
        text_y = y + height - padding
        for text, font_size, color in lines:
            text_y -= font_size
            blf.size(0, font_size)
            blf.position(0, x + padding, text_y, 0)
            blf.color(0, *color)
            blf.draw(0, text)
            text_y -= gap
    finally:
        blf.disable(0, blf.SHADOW)
        gpu.state.blend_set(blend)
