"""Real mesh writes and foreground HUD draw submission; no user files are changed.

Run with --factory-startup --python tests/blender_benchmark.py -- --label before.
Add --verify to enforce work-count budgets (timings are informational).
"""
import argparse
import json
import os
from pathlib import Path
import statistics
import sys
from time import perf_counter
import traceback
from types import SimpleNamespace

import addon_utils
import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
addon_utils.enable(ROOT.name, default_set=True)
from quick_crease_weight import hud, preferences
from quick_crease_weight.mesh_data import WeightEdit

parser = argparse.ArgumentParser()
parser.add_argument("--label", default="current")
parser.add_argument("--verify", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
output = ROOT / "tests" / "artifacts" / f"performance-{args.label}.json"
output.parent.mkdir(parents=True, exist_ok=True)
area = next(item for item in bpy.context.screen.areas if item.type == "VIEW_3D")
region = next(item for item in area.regions if item.type == "WINDOW")
prefs = preferences.get_preferences(bpy.context)
result = {"blender": bpy.app.version_string, "mesh": {}, "hud": {}}
updates = 0
real_update = WeightEdit._update


def counted_update(snapshot):
    global updates
    updates += 1
    real_update(snapshot)


WeightEdit._update = staticmethod(counted_update)


def timed(function, count):
    samples = []
    for index in range(count):
        start = perf_counter()
        function(index)
        samples.append((perf_counter() - start) * 1000)
    return round(statistics.median(samples), 6)


def mesh_benchmark():
    global updates
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    mesh = bpy.data.meshes.new("benchmark_grid")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=316, y_segments=316, size=10)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("benchmark_grid", mesh)
    bpy.context.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    for kind in ("crease", "bevel_weight"):
        for domain in ("POINT", "EDGE"):
            bpy.context.tool_settings.mesh_select_mode = (domain == "POINT", domain == "EDGE", False)
            bpy.ops.mesh.select_all(action="SELECT")
            setup_ms = timed(lambda _: WeightEdit(bpy.context, kind), 3)
            edit = WeightEdit(bpy.context, kind)
            first_ms = timed(lambda _: edit.apply(0.25), 1)
            updates = 0
            repeat_ms = timed(lambda _: edit.apply(0.25), 20)
            repeat_updates = updates
            updates = 0
            changed_ms = timed(lambda i: edit.apply(0.75 if i % 2 == 0 else 0.25), 20)
            changed_updates = updates
            snapshot = edit.snapshots[0]
            sequence = snapshot.bm.verts if domain == "POINT" else snapshot.bm.edges
            layer = sequence.layers.float.get(edit.name)
            assert all(element[layer] == 0.25 for element in sequence)
            restore_ms = timed(lambda _: edit.restore(), 1)
            assert sequence.layers.float.get(edit.name) is None
            result["mesh"][f"{kind}_{domain.lower()}"] = {
                "selected": edit.count, "setup_ms": setup_ms, "first_apply_ms": first_ms,
                "repeat_apply_ms": repeat_ms, "repeat_updates_20": repeat_updates,
                "changed_apply_ms": changed_ms, "changed_updates_20": changed_updates,
                "restore_ms": restore_ms,
            }
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cube_add()
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")


counts = {"batches": 0, "measurements": 0}
real_batch = hud.batch_for_shader
real_measure = hud.text_width


def counted_batch(*a, **kw):
    counts["batches"] += 1
    return real_batch(*a, **kw)


def counted_measure(*a, **kw):
    counts["measurements"] += 1
    return real_measure(*a, **kw)


hud.batch_for_shader = counted_batch
hud.text_width = counted_measure
operator = SimpleNamespace(_area=area, _region=region, _edit=SimpleNamespace(domain="POINT", count=8),
                           _mouse_region=(300, 300), attribute_kind="crease", display_name="Crease", value=0.5)
scenarios = iter(("idle", "value_changes", "cursor_moves"))
scenario = None
samples = []
frame = 0
handle = None


def finish(error=None):
    if handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(handle, "WINDOW")
    operator.__dict__.pop("_hud", None)
    if error:
        result["error"] = error
    result["success"] = error is None
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)
    if error:
        os._exit(1)
    bpy.ops.wm.quit_blender()


def draw_sample():
    global frame
    if bpy.context.area != area or bpy.context.region != region or scenario is None:
        return
    try:
        if scenario == "value_changes":
            operator.value = 0.2 + (frame % 60) * 0.01
        if scenario == "cursor_moves":
            operator._mouse_region = (220 + frame, 240 + frame // 2)
        if frame == 8:
            counts.update(batches=0, measurements=0)
        start = perf_counter()
        hud.draw(operator)
        elapsed = (perf_counter() - start) * 1000
        if frame >= 8:
            samples.append(elapsed)
        frame += 1
    except Exception:
        finish(traceback.format_exc())


def tick():
    global scenario, frame, samples
    try:
        if frame >= 88:
            result["hud"][scenario] = {"median_submit_ms": round(statistics.median(samples), 6),
                                       "frames": len(samples), **counts}
            scenario = None
        if scenario is None:
            scenario = next(scenarios, None)
            if scenario is None:
                if args.verify:
                    assert all(case["repeat_updates_20"] == 0 for case in result["mesh"].values()), "Repeated values updated meshes"
                    assert all(case["changed_updates_20"] == 20 for case in result["mesh"].values()), "Changed values were skipped"
                    for name, case in result["hud"].items():
                        assert case["measurements"] == 0, f"Repeated text measurement: {name}"
                        assert case["batches"] <= (case["frames"] if name == "value_changes" else 0), f"Rebuilt static geometry: {name}"
                finish()
                return None
            prefs.hud_anchor = "CURSOR" if scenario == "cursor_moves" else "BOTTOM"
            frame, samples = 0, []
        area.tag_redraw()
        return 0.01
    except Exception:
        finish(traceback.format_exc())
        return None


def start():
    global handle
    try:
        with bpy.context.temp_override(area=area, region=region):
            mesh_benchmark()
        handle = bpy.types.SpaceView3D.draw_handler_add(draw_sample, (), "WINDOW", "POST_PIXEL")
        bpy.app.timers.register(tick, first_interval=0.1)
    except Exception:
        finish(traceback.format_exc())
    return None


bpy.app.timers.register(start, first_interval=2.0)
