"""Real-window i18n checks; run with --factory-startup --enable-event-simulate.

Uses Blender's own draw/event APIs, never saves preferences, and exits when done.
Screenshots and results are written under tests/artifacts/i18n-<version>/.
"""
import json
import os
from pathlib import Path
import sys
import traceback
from types import SimpleNamespace

import addon_utils
import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "artifacts" / ("i18n-" + ".".join(map(str, bpy.app.version)))
OUTPUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT.parent))
addon_utils.enable(ROOT.name, default_set=True)
from quick_crease_weight import hud, operators, preferences, translation
from quick_crease_weight.mesh_data import WeightEdit

window = bpy.context.window
area = next(item for item in window.screen.areas if item.type == "VIEW_3D")
region = next(item for item in area.regions if item.type == "WINDOW")
view = bpy.context.preferences.view
prefs = preferences.get_preferences(bpy.context)
checks, draw_errors = [], []
original_draw = hud.draw
original_rebuild = hud.HudRenderer.rebuild
original_status = operators.WeightOperator._draw_status
rebuilds = 0
last_rebuilds = None
pref_draws = 0
status_draws = 0


def checked_draw(operator):
    try:
        original_draw(operator)
    except Exception:
        draw_errors.append(traceback.format_exc())


def counted_rebuild(self, *args):
    global rebuilds
    rebuilds += 1
    return original_rebuild(self, *args)


def checked_status(self, header, context):
    global status_draws
    try:
        original_status(self, header, context)
        if isinstance(header, bpy.types.Header):
            status_draws += 1
    except Exception:
        draw_errors.append(traceback.format_exc())


hud.draw = checked_draw
hud.HudRenderer.rebuild = counted_rebuild
operators.WeightOperator._draw_status = checked_status


class QCW_PT_translation_preferences(bpy.types.Panel):
    bl_idname = "QCW_PT_translation_preferences"
    bl_label = "Quick Crease Weight"
    bl_space_type = "PREFERENCES"
    bl_region_type = "WINDOW"

    def draw(self, context):
        global pref_draws
        try:
            prefs.draw_settings(self.layout, context)
            pref_draws += 1
        except Exception:
            draw_errors.append(traceback.format_exc())


def set_language(language, interface=True):
    view.language = language
    view.use_translate_interface = interface


def setup():
    set_language("en_US")
    view.use_translate_tooltips = True
    view.use_translate_reports = True
    for obj in bpy.context.scene.objects:
        if obj.type in {"CAMERA", "LIGHT"}:
            obj.hide_set(True)
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        assert bpy.ops.mesh.quick_crease("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
    operators.ACTIVE[0]._set_value(0.5)


def check_hud(name, chinese, expect_rebuild=True):
    global last_rebuilds
    assert not draw_errors, "\n".join(draw_errors)
    assert status_draws > 0, "Blender did not draw the status callback"
    assert len(operators.ACTIVE) == 1
    op = operators.ACTIVE[0]
    renderer = op._hud
    assert renderer is not None
    texts = [item[0] for item in renderer.texts]
    title = translation.tr(op.display_name)
    assert texts[0] == title, texts
    assert ("左右拖动" if chinese else "Drag left/right") in texts, texts
    domain = "Vertices" if op._edit.domain == "POINT" else "Edges"
    assert texts[1] == f"{translation.tr(domain)}  ·  {op._edit.count}", texts
    # Check actual measured text bounds, including the cached title and badge.
    for text, x, y, size, _color in renderer.texts:
        assert x >= 0 and y >= 0, (name, text, x, y)
        assert x + hud.text_width(text, size) <= renderer.width + 2, (name, text, renderer.width)
    title_item, badge_item = renderer.texts[:2]
    assert title_item[1] + hud.text_width(title_item[0], title_item[3]) < badge_item[1]
    bounds = hud.viewport_bounds(area, region)
    assert renderer.width <= bounds[2] and renderer.height <= bounds[3]
    if last_rebuilds is not None:
        assert (rebuilds > last_rebuilds) == expect_rebuild, (name, rebuilds, last_rebuilds)
    last_rebuilds = rebuilds
    labels = []
    header = SimpleNamespace(layout=SimpleNamespace(label=lambda **kwargs: labels.append(kwargs)))
    op._draw_status(header, bpy.context)
    assert title in labels[0]["text"]
    assert ("左键/Enter 确认" if chinese else "LMB/Enter: confirm") in labels[0]["text"]
    assert labels[0]["translate"] is False
    bpy.ops.screen.screenshot(filepath=str(OUTPUT / (name + ".png")))
    checks.append({"name": name, "locale": bpy.app.translations.locale, "texts": texts,
                   "status": labels[0]["text"], "rebuilds": rebuilds})


def check_native_and_flags():
    source = "Quick Crease"
    tip = operators.QCW_OT_crease.bl_description
    assert translation.tr(source, "Operator") == "快速折痕"
    assert bpy.app.translations.pgettext_tip(tip) == translation.ZH_CN[tip]
    assert translation.rpt("Select vertices or edges first") == "请先选择顶点或边"
    for prop in preferences.QCW_Preferences.bl_rna.properties:
        if prop.identifier in {"rna_type", "bl_idname"}:
            continue
        assert translation.tr(prop.name) != prop.name, prop.name
        if prop.description:
            assert bpy.app.translations.pgettext_tip(prop.description) != prop.description
        if prop.type == "ENUM":
            for item in prop.enum_items:
                assert translation.tr(item.name) != item.name, item.name
                assert bpy.app.translations.pgettext_tip(item.description) != item.description
    view.use_translate_interface = False
    assert translation.tr(source, "Operator") == source
    # Tooltips and reports remain independent of the interface switch.
    assert bpy.app.translations.pgettext_tip(tip) == translation.ZH_CN[tip]
    assert translation.rpt("Select vertices or edges first") == "请先选择顶点或边"
    view.use_translate_tooltips = False
    view.use_translate_reports = False
    assert bpy.app.translations.pgettext_tip(tip) == tip
    assert translation.rpt("Select vertices or edges first") == "Select vertices or edges first"
    checks.append({"name": "native labels, enum items, tooltips, and independent translation flags"})


def switch_to_bevel():
    operators.cancel_active()
    set_language("en_US")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.context.tool_settings.mesh_select_mode = (False, True, False)
        assert bpy.ops.mesh.quick_bevel_weight("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
    operators.ACTIVE[0]._set_value(0.7)


def check_system_language():
    locale = bpy.app.translations.locale
    check_hud("system-language", locale.startswith(("zh_HANS", "zh_CN")),
              expect_rebuild=locale != checks[-1]["locale"])


def check_errors_and_registration():
    operators.cancel_active()
    set_language("zh_HANS")
    view.use_translate_tooltips = True
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        for enabled in (True, False):
            view.use_translate_reports = enabled
            bpy.ops.mesh.select_all(action="DESELECT")
            try:
                WeightEdit(bpy.context, "crease")
                raise AssertionError("Empty selection was accepted")
            except ValueError as error:
                assert str(error) == ("请先选择顶点或边" if enabled else "Select vertices or edges first")
            bpy.ops.mesh.select_all(action="SELECT")
            bm = bmesh.from_edit_mesh(bpy.context.object.data)
            layer = bm.verts.layers.int.new("crease_vert")
            bmesh.update_edit_mesh(bpy.context.object.data)
            try:
                WeightEdit(bpy.context, "crease")
                raise AssertionError("Conflicting attribute was accepted")
            except ValueError as error:
                suffix = "已存在，但不是正确域的浮点属性" if enabled else "already exists but is not a float attribute on the correct domain"
                assert str(error) == f"{bpy.context.object.name}: crease_vert {suffix}", str(error)
            finally:
                bm.verts.layers.int.remove(layer)
                bmesh.update_edit_mesh(bpy.context.object.data)
    addon_utils.disable(ROOT.name, default_set=True)
    assert translation.tr("Quick Crease", "Operator") == "Quick Crease"
    addon_utils.enable(ROOT.name, default_set=True)
    assert translation.tr("Quick Crease", "Operator") == "快速折痕"
    checks.append({"name": "localized errors, report toggle, disable and re-enable"})


def show_preferences():
    global prefs
    prefs = preferences.get_preferences(bpy.context)
    bpy.utils.register_class(QCW_PT_translation_preferences)
    area.type = "PREFERENCES"
    bpy.context.preferences.active_section = "ADDONS"
    bpy.context.window_manager.addon_search = "Quick Crease Weight"
    window.event_simulate(type="MOUSEMOVE", value="NOTHING", x=area.x + 5, y=area.y + 5)


def capture_preferences(name):
    assert pref_draws > 0 and not draw_errors, draw_errors
    bpy.ops.screen.screenshot(filepath=str(OUTPUT / (name + ".png")))
    checks.append({"name": name})


def finish():
    assert not draw_errors, "\n".join(draw_errors)
    (OUTPUT / "result.json").write_text(json.dumps({"success": True, "blender": bpy.app.version_string,
        "checks": checks, "preference_draws": pref_draws}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Translation checks passed: {bpy.app.version_string}; {len(checks)} scenarios", flush=True)
    bpy.ops.wm.quit_blender()


steps = iter((
    lambda: window.event_simulate(type="ESC", value="PRESS", x=region.x + region.width // 2,
                                  y=region.y + region.height // 2),
    setup,
    lambda: check_hud("crease-en", False),
    lambda: check_hud("crease-en-cached", False, expect_rebuild=False),
    lambda: set_language("zh_HANS"),
    lambda: check_hud("crease-zh", True),
    check_native_and_flags,
    lambda: check_hud("interface-disabled", False),
    lambda: set_language("en_US"),
    lambda: check_hud("back-to-en", False),
    lambda: set_language("DEFAULT"),
    check_system_language,
    switch_to_bevel,
    lambda: check_hud("bevel-en", False),
    lambda: set_language("zh_HANS"),
    lambda: check_hud("bevel-zh", True),
    check_errors_and_registration,
    show_preferences,
    lambda: capture_preferences("preferences-zh"),
    lambda: set_language("en_US"),
    lambda: capture_preferences("preferences-en"),
    finish,
))


def tick():
    try:
        next(steps)()
        area.tag_redraw()
        return 0.8
    except StopIteration:
        return None
    except Exception:
        error = traceback.format_exc()
        (OUTPUT / "result.json").write_text(json.dumps({"success": False, "error": error,
            "draw_errors": draw_errors, "checks": checks}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(error, flush=True)
        os._exit(1)


bpy.app.timers.register(tick, first_interval=3.0)
