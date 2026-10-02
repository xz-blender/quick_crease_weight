# SPDX-License-Identifier: GPL-3.0-or-later
"""Selection-aware mesh crease and bevel weight tools."""

bl_info = {
    "name": "Quick Crease Weight",
    "author": "WXZ",
    "version": (1, 2, 1),
    "blender": (4, 2, 0),
    "location": "3D View > Mesh Edit Mode",
    "description": "Quickly adjust vertex or edge creases and bevel weights with custom shortcuts and a HUD",
    "category": "Mesh",
}

import bpy

from . import keymaps, operators, preferences, translation

CLASSES = (preferences.QCW_Preferences, *operators.CLASSES)


def register():
    translation.register()
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    keymaps.register()


def unregister():
    operators.cancel_active()
    keymaps.unregister()
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    translation.unregister()
