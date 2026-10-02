# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import rna_keymap_ui

KEYMAPS = []
BINDINGS = (
    ("mesh.quick_crease", "折痕", False),
    ("mesh.quick_bevel_weight", "倒角权重", True),
)


def register():
    unregister()
    config = bpy.context.window_manager.keyconfigs.addon
    if config is None:
        return
    keymap = config.keymaps.new(name="Mesh", space_type="EMPTY")
    for identifier, _label, ctrl in BINDINGS:
        item = keymap.keymap_items.new(identifier, "E", "PRESS", shift=True, ctrl=ctrl)
        KEYMAPS.append((keymap, item))


def unregister():
    for keymap, item in KEYMAPS:
        try:
            keymap.keymap_items.remove(item)
        except (ReferenceError, RuntimeError):
            pass
    KEYMAPS.clear()


def draw(layout, context):
    # Edit the effective user keymap: Blender persists these overrides in user preferences.
    config = context.window_manager.keyconfigs.user
    keymap = config.keymaps.get("Mesh") if config else None
    for identifier, label, _ctrl in BINDINGS:
        box = layout.box()
        box.label(text=label)
        items = [item for item in keymap.keymap_items if item.idname == identifier] if keymap else []
        if items:
            for item in items:
                box.context_pointer_set("keymap", keymap)
                rna_keymap_ui.draw_kmi([], config, keymap, item, box, 0)
        else:
            box.label(text="快捷键将在 Blender 更新键位配置后显示", icon="INFO")
    if keymap and any(item.active and item.idname == "pie.shift_e" for item in keymap.keymap_items):
        layout.label(text="检测到原饼菜单快捷键：请禁用旧绑定或为本插件改键。", icon="ERROR")
