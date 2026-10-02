# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
import rna_keymap_ui

KEYMAPS = []
BINDINGS = (
    ("mesh.quick_crease", "Crease", False),
    ("mesh.quick_bevel_weight", "Bevel Weight", True),
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
            box.label(text="Shortcuts will appear after Blender updates its key configuration", icon="INFO")
