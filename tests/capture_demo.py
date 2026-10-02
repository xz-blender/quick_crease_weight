"""Capture a real Blender demo in a disposable factory-startup window.

Run with --enable-event-simulate --python tests/capture_demo.py.
Frames and a timing manifest are written to tests/artifacts/demo/.
"""
import json
import os
from pathlib import Path
import sys
import traceback

import addon_utils
import blf
import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "artifacts" / "demo"
OUTPUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT.parent))
addon_utils.enable(ROOT.name, default_set=True)
from quick_crease_weight import operators, preferences

window = bpy.context.window
area = next(item for item in window.screen.areas if item.type == "VIEW_3D")
region = next(item for item in area.regions if item.type == "WINDOW")
prefs = preferences.get_preferences(bpy.context)
title = "QUICK CREASE WEIGHT"
subtitle = "Vertex creases and edge bevel weights"
accent = (1.0, 0.5, 0.15, 1.0)
frames = []
handle = None
steps = []


def send(kind, value="PRESS", dx=0, **modifiers):
    window.event_simulate(type=kind, value=value, x=region.x + region.width // 2 + dx,
                          y=region.y + int(region.height * 0.65), **modifiers)


def capture(duration=0.10):
    path = OUTPUT / f"frame-{len(frames):04d}.png"
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.screen.screenshot_area(filepath=str(path))
    frames.append({"file": path.name, "duration": duration})


def title_draw():
    if bpy.context.area != area:
        return
    scale = bpy.context.preferences.system.ui_scale
    for text, size, y, color in ((title, 23, region.height - 50 * scale, accent),
                               (subtitle, 13, region.height - 76 * scale, (0.78, 0.82, 0.9, 1))):
        blf.size(0, size * scale)
        width = blf.dimensions(0, text)[0]
        blf.position(0, (region.width - width) / 2, y, 0)
        blf.color(0, *color)
        blf.draw(0, text)


def setup():
    global area, region, handle
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.screen.screen_full_area(use_hide_panels=True)
    area = next(item for item in window.screen.areas if item.type == "VIEW_3D")
    region = next(item for item in area.regions if item.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        bpy.ops.mesh.primitive_cube_add(size=2.4)
        obj = bpy.context.object
        obj.name = "Quick Crease Weight Demo"
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        obj.modifiers.new("Crease Preview", "SUBSURF").levels = 3
        bevel = obj.modifiers.new("Weight Preview", "BEVEL")
        bevel.limit_method = "WEIGHT"
        bevel.width = 0.35
        bevel.segments = 8
        bevel.show_viewport = False
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action="SELECT")
    space = area.spaces.active
    space.show_region_toolbar = False
    space.show_region_ui = False
    space.show_gizmo = False
    space.overlay.show_floor = False
    space.overlay.show_axis_x = False
    space.overlay.show_axis_y = False
    space.overlay.show_cursor = False
    space.overlay.show_text = False
    space.overlay.show_faces = False
    space.show_region_hud = False
    space.shading.light = "STUDIO"
    space.shading.color_type = "SINGLE"
    space.shading.single_color = (0.48, 0.53, 0.63)
    space.shading.background_type = "VIEWPORT"
    space.shading.background_color = (0.025, 0.032, 0.048)
    space.region_3d.view_distance = 7.8
    space.region_3d.view_location = (0, 0, -0.6)
    prefs.hud_offset_y = 25
    prefs.hud_font_size = 38
    handle = bpy.types.SpaceView3D.draw_handler_add(title_draw, (), "WINDOW", "POST_PIXEL")
    send("MOUSEMOVE", "NOTHING")


def start_crease():
    global title, subtitle, accent
    title, subtitle = "CREASE", "Shift + E  /  Vertex mode  /  Drag to adjust"
    accent = (1.0, 0.5, 0.15, 1.0)
    send("E", shift=True)


def release_crease():
    assert operators.ACTIVE[0].attribute_kind == "crease"
    send("E", "RELEASE", shift=True)
    send("LEFT_SHIFT", "RELEASE")


def start_bevel():
    global title, subtitle, accent
    assert not operators.ACTIVE
    title, subtitle = "BEVEL WEIGHT", "Ctrl + Shift + E  /  Edge mode  /  Drag to adjust"
    accent = (0.25, 0.75, 1.0, 1.0)
    obj = bpy.context.object
    obj.modifiers["Crease Preview"].show_viewport = False
    obj.modifiers["Weight Preview"].show_viewport = True
    bm = bmesh.from_edit_mesh(obj.data)
    for face in bm.faces:
        face.smooth = False
    bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)
    send("MOUSEMOVE", "NOTHING")
    send("E", ctrl=True, shift=True)


def release_bevel():
    assert operators.ACTIVE[0].attribute_kind == "bevel_weight"
    send("E", "RELEASE", ctrl=True, shift=True)
    send("LEFT_CTRL", "RELEASE", shift=True)
    send("LEFT_SHIFT", "RELEASE")


def verify_value(value):
    assert len(operators.ACTIVE) == 1
    assert abs(operators.ACTIVE[0].value - value) < 0.001
    return True


def key_hint(key, message):
    global subtitle
    subtitle = message
    send(key, **{"ctrl" if key == "LEFT_CTRL" else "alt": True})


def finish():
    assert not operators.ACTIVE
    bpy.types.SpaceView3D.draw_handler_remove(handle, "WINDOW")
    (OUTPUT / "frames.json").write_text(json.dumps({"blender": bpy.app.version_string,
                                                  "frames": frames}, indent=2), encoding="utf-8")
    lines = []
    for frame in frames:
        lines.extend([f"file '{frame['file']}'", f"duration {frame['duration']:.3f}"])
    lines.append(f"file '{frames[-1]['file']}'")
    (OUTPUT / "frames.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Captured {len(frames)} frames", flush=True)
    bpy.ops.wm.quit_blender()


def add(action, delay=0.12):
    steps.append((action, delay))


add(lambda: send("ESC"), 0.5)
add(setup, 1.2)
add(start_crease, 0.35)
add(release_crease, 0.2)
add(lambda: capture(1.0))
for position in range(0, 201, 8):
    add(lambda x=position: send("MOUSEMOVE", "NOTHING", dx=x), 0.10)
    add(lambda: capture(0.08), 0.02)
add(lambda: verify_value(1.0))
add(lambda: capture(0.8))
add(lambda: send("RET"), 0.3)
add(start_bevel, 0.35)
add(release_bevel, 0.2)
add(lambda: capture(1.0))
for position in range(0, 151, 6):
    add(lambda x=position: send("MOUSEMOVE", "NOTHING", dx=x), 0.10)
    add(lambda: capture(0.08), 0.02)
add(lambda: verify_value(0.75))
add(lambda: capture(0.8))
add(lambda: key_hint("LEFT_CTRL", "Ctrl  /  Set selected weights to 1.00"), 0.2)
add(lambda: verify_value(1.0))
add(lambda: capture(1.0))
add(lambda: send("LEFT_CTRL", "RELEASE"))
add(lambda: key_hint("LEFT_ALT", "Alt  /  Reset selected weights to 0.00"), 0.2)
add(lambda: verify_value(0.0))
add(lambda: capture(1.0))
add(lambda: send("LEFT_ALT", "RELEASE"))
add(lambda: send("RET"), 0.2)
add(finish)
iterator = iter(steps)


def tick():
    try:
        action, delay = next(iterator)
        with bpy.context.temp_override(window=window, area=area, region=region):
            action()
        area.tag_redraw()
        return delay
    except StopIteration:
        return None
    except Exception:
        (OUTPUT / "error.txt").write_text(traceback.format_exc(), encoding="utf-8")
        print(traceback.format_exc(), flush=True)
        os._exit(1)


bpy.app.timers.register(tick, first_interval=3.0)
