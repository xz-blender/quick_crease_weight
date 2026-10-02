"""Run in factory-startup Blender; does not save or alter user preferences."""
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import addon_utils
import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
addon = importlib.import_module(ROOT.name)
addon_utils.enable(ROOT.name, default_set=True)
from quick_crease_weight import keymaps, operators, preferences
from quick_crease_weight.mesh_data import WeightEdit


def event(kind, value="PRESS", x=100, shift=False, ctrl=False, alt=False):
    return SimpleNamespace(type=kind, value=value, mouse_x=x, mouse_region_x=x,
                           mouse_region_y=200, shift=shift, ctrl=ctrl, alt=alt)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        operators.cancel_active()
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        mesh = bpy.data.meshes.new("test_mesh")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [], [(0, 1, 2, 3)])
        self.obj = bpy.data.objects.new("test_object", mesh)
        bpy.context.collection.objects.link(self.obj)
        self.obj.select_set(True)
        bpy.context.view_layer.objects.active = self.obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action="SELECT")
        self.bm = bmesh.from_edit_mesh(mesh)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()

    def tearDown(self):
        operators.cancel_active()
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

    def values(self, name, domain="POINT", bm=None):
        bm = bm if bm is not None else self.bm
        elements = bm.verts if domain == "POINT" else bm.edges
        layer = elements.layers.float.get(name)
        self.assertIsNotNone(layer)
        return [element[layer] for element in elements]

    def test_all_four_attributes_and_face_domain(self):
        for kind in ("crease", "bevel_weight"):
            for mode, suffix, domain in (((True, False, False), "vert", "POINT"),
                                         ((False, True, False), "edge", "EDGE"),
                                         ((False, False, True), "edge", "EDGE")):
                with self.subTest(kind=kind, mode=mode):
                    bpy.context.tool_settings.mesh_select_mode = mode
                    edit = WeightEdit(bpy.context, kind)
                    edit.apply(0.625)
                    self.assertEqual(self.values(f"{kind}_{suffix}", domain), [0.625] * 4)
                    self.assertEqual(edit.domain, domain)
                    edit.restore()

    def test_cancel_restores_mixed_values_and_untouched_elements(self):
        layer = self.bm.verts.layers.float.new("crease_vert")
        original = [0.125, 0.25, 0.75, 1.0]
        for vertex, value in zip(self.bm.verts, original):
            vertex[layer] = value
        self.bm.verts[3].select_set(False)
        edit = WeightEdit(bpy.context, "crease")
        self.assertEqual(edit.initial_value, 0.375)
        edit.apply(0.5)
        self.assertEqual(self.values("crease_vert"), [0.5, 0.5, 0.5, 1.0])
        edit.restore()
        self.assertEqual(self.values("crease_vert"), original)

    def test_cancel_removes_new_layer_and_clamps(self):
        edit = WeightEdit(bpy.context, "bevel_weight")
        self.assertIsNone(self.bm.verts.layers.float.get("bevel_weight_vert"))
        edit.apply(20)
        self.assertEqual(self.values("bevel_weight_vert"), [1.0] * 4)
        edit.apply(-10)
        self.assertEqual(self.values("bevel_weight_vert"), [0.0] * 4)
        edit.restore()
        self.assertIsNone(self.bm.verts.layers.float.get("bevel_weight_vert"))

    def test_repeated_values_skip_updates_without_skipping_first_average(self):
        layer = self.bm.verts.layers.float.new("crease_vert")
        original = [0.25, 0.75, 0.25, 0.75]
        for element, value in zip(self.bm.verts, original):
            element[layer] = value
        edit = WeightEdit(bpy.context, "crease")
        with patch.object(WeightEdit, "_update", wraps=WeightEdit._update) as update:
            edit.apply(edit.initial_value)
            self.assertEqual(self.values("crease_vert"), [0.5] * 4)
            edit.apply(0.5)
            self.assertEqual(update.call_count, 1)
            edit.apply(3)
            edit.apply(2)
            self.assertEqual(update.call_count, 2)
            self.assertEqual(self.values("crease_vert"), [1] * 4)
        edit.restore()
        self.assertEqual(self.values("crease_vert"), original)
        edit.apply(0.5)
        self.assertEqual(self.values("crease_vert"), [0.5] * 4)
        edit.restore()

    def test_layer_creation_between_writes_preserves_targets_and_cancel(self):
        edit = WeightEdit(bpy.context, "crease")
        edit.apply(0.25)
        self.bm.verts.layers.float.new("unrelated_attribute")
        edit.apply(0.75)
        self.assertEqual(self.values("crease_vert"), [0.75] * 4)
        edit.restore()
        self.assertIsNone(self.bm.verts.layers.float.get("crease_vert"))
        self.assertIsNotNone(self.bm.verts.layers.float.get("unrelated_attribute"))

    def test_hidden_and_empty_selection(self):
        self.bm.verts[0].hide = True
        edit = WeightEdit(bpy.context, "crease")
        self.assertEqual(edit.count, 3)
        edit.apply(1)
        self.assertEqual(self.values("crease_vert"), [0, 1, 1, 1])
        bpy.ops.mesh.select_all(action="DESELECT")
        with self.assertRaisesRegex(ValueError, "请先选择"):
            WeightEdit(bpy.context, "crease")

    def test_wrong_attribute_type_does_not_mutate(self):
        self.bm.verts.layers.int.new("crease_vert")
        bmesh.update_edit_mesh(self.obj.data)
        with self.assertRaisesRegex(ValueError, "浮点属性"):
            WeightEdit(bpy.context, "crease")
        self.assertIsNone(self.bm.verts.layers.float.get("crease_vert"))

    def test_multi_object_and_shared_data(self):
        bpy.ops.object.mode_set(mode="OBJECT")
        other = self.obj.copy()
        other.data = self.obj.data.copy()
        bpy.context.collection.objects.link(other)
        other.select_set(True)
        linked = self.obj.copy()
        bpy.context.collection.objects.link(linked)
        linked.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        edit = WeightEdit(bpy.context, "crease")
        self.assertEqual(len(edit.snapshots), 2)
        self.assertEqual(edit.count, 8)
        edit.apply(0.75)
        for snapshot in edit.snapshots:
            self.assertEqual(self.values("crease_vert", bm=snapshot.bm), [0.75] * 4)
        edit.restore()
        for snapshot in edit.snapshots:
            self.assertIsNone(snapshot.bm.verts.layers.float.get("crease_vert"))

    def test_real_registered_execute_and_poll(self):
        for identifier, attribute in (("quick_crease", "crease_vert"),
                                       ("quick_bevel_weight", "bevel_weight_vert")):
            result = getattr(bpy.ops.mesh, identifier)(value=0.5)
            self.assertEqual(result, {"FINISHED"})
            self.assertEqual(self.values(attribute), [0.5] * 4)
        bpy.ops.object.mode_set(mode="OBJECT")
        self.assertFalse(bpy.ops.mesh.quick_crease.poll())

    def test_preferences_and_registration_cycle(self):
        prefs = preferences.get_preferences(bpy.context)
        self.assertIsNotNone(prefs)
        prefs.hud_font_size = 48
        prefs.hud_anchor = "CURSOR"
        self.assertEqual(prefs.hud_font_size, 48)
        self.assertEqual(prefs.hud_anchor, "CURSOR")
        self.assertEqual(len(keymaps.KEYMAPS), 2)
        for _keymap, item in keymaps.KEYMAPS:
            self.assertEqual(item.type, "E")
            self.assertTrue(item.shift)
            self.assertEqual(item.ctrl, item.idname == "mesh.quick_bevel_weight")
        addon.unregister()
        self.assertEqual(keymaps.KEYMAPS, [])
        addon.register()
        self.assertEqual(len(keymaps.KEYMAPS), 2)

    def make_modal(self, kind="crease", initial_event=None):
        # A plain harness executes the production modal methods without putting
        # synthetic operators into Blender's real window event queue.
        class Harness(operators.WeightOperator):
            attribute_kind = kind
            display_name = "测试"

        op = Harness()
        op._edit = WeightEdit(bpy.context, kind)
        op.value = op._edit.initial_value
        op._area, op._region, op._workspace = bpy.context.area, bpy.context.region, bpy.context.workspace
        op._origin_x, op._origin_value = 100, op.value
        op._blocked_modifiers = set()
        if initial_event:
            op._blocked_modifiers = {key for key in ("shift", "ctrl", "alt") if getattr(initial_event, key)}
        op._closed, op._navigating, op._handle = False, False, None
        op._sensitivity = 0.005
        operators.ACTIVE.append(op)
        return op

    def test_modal_shortcut_modifiers_snap_ctrl_alt_cancel(self):
        op = self.make_modal("bevel_weight", event("E", shift=True, ctrl=True))
        op.modal(bpy.context, event("MOUSEMOVE", x=150, shift=True, ctrl=True))
        self.assertAlmostEqual(op.value, 0.25)
        op.modal(bpy.context, event("LEFT_CTRL", "RELEASE", x=150, shift=True))
        op.modal(bpy.context, event("LEFT_SHIFT", "RELEASE", x=150))
        op.modal(bpy.context, event("LEFT_SHIFT", x=150, shift=True))
        op.modal(bpy.context, event("MOUSEMOVE", x=172, shift=True))
        self.assertAlmostEqual(op.value, 0.4)
        op.modal(bpy.context, event("LEFT_CTRL", x=172, ctrl=True))
        self.assertEqual(op.value, 1)
        op.modal(bpy.context, event("LEFT_CTRL", "RELEASE", x=172))
        op.modal(bpy.context, event("LEFT_ALT", x=172, alt=True))
        self.assertEqual(op.value, 0)
        op.modal(bpy.context, event("LEFT_ALT", "RELEASE", x=172))
        op.modal(bpy.context, event("MOUSEMOVE", x=192))
        self.assertAlmostEqual(op.value, 0.1)
        self.assertEqual(op.modal(bpy.context, event("ESC")), {"CANCELLED"})
        self.assertIsNone(self.bm.verts.layers.float.get("bevel_weight_vert"))
        self.assertEqual(operators.ACTIVE, [])

    def test_modal_confirm_navigation_and_disable(self):
        op = self.make_modal()
        op.modal(bpy.context, event("MIDDLEMOUSE"))
        op.modal(bpy.context, event("MOUSEMOVE", x=300))
        self.assertFalse(op._edit.changed)
        op.modal(bpy.context, event("MIDDLEMOUSE", "RELEASE", x=300))
        op.modal(bpy.context, event("MOUSEMOVE", x=350))
        self.assertEqual(op.value, 0.25)
        self.assertEqual(op.modal(bpy.context, event("RET")), {"FINISHED"})
        self.assertIsNone(op._edit)
        self.assertIsNone(op._hud)
        self.assertEqual(self.values("crease_vert"), [0.25] * 4)
        op = self.make_modal()
        op.modal(bpy.context, event("LEFT_CTRL", ctrl=True))
        operators.cancel_active()
        self.assertEqual(self.values("crease_vert"), [0.25] * 4)
        self.assertEqual(operators.ACTIVE, [])

    def test_stationary_mouse_preserves_mixed_values_and_repeat_snap_skips_update(self):
        layer = self.bm.verts.layers.float.new("crease_vert")
        original = [0.125, 0.25, 0.75, 0.875]
        for element, value in zip(self.bm.verts, original):
            element[layer] = value
        op = self.make_modal()
        op.modal(bpy.context, event("MOUSEMOVE", x=100))
        self.assertFalse(op._edit.changed)
        self.assertEqual(self.values("crease_vert"), original)
        with patch.object(WeightEdit, "_update", wraps=WeightEdit._update) as update:
            op.modal(bpy.context, event("MOUSEMOVE", x=120, shift=True))
            op.modal(bpy.context, event("MOUSEMOVE", x=121, shift=True))
            op.modal(bpy.context, event("MOUSEMOVE", x=122, shift=True))
            self.assertEqual(update.call_count, 1)
        op.modal(bpy.context, event("ESC"))
        self.assertEqual(self.values("crease_vert"), original)


area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
region = next(region for region in area.regions if region.type == "WINDOW")
with bpy.context.temp_override(area=area, region=region):
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrationTests))
addon_utils.disable(ROOT.name, default_set=True)
print(f"Blender {bpy.app.version_string}: {result.testsRun} checks; success={result.wasSuccessful()}")
if not result.wasSuccessful():
    raise SystemExit(1)
