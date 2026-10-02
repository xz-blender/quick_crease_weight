# SPDX-License-Identifier: GPL-2.0-or-later
"""Independent mesh crease and bevel weight tools, extracted from wxz_pie_menus."""

bl_info = {
    "name": "Quick Crease Weight",
    "author": "WXZ",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D View > Mesh Edit Mode",
    "description": "根据点/边选择模式快速调整折痕与倒角权重，支持自定义快捷键与 HUD",
    "category": "Mesh",
}

import bpy

from . import keymaps, operators, preferences

CLASSES = (preferences.QCW_Preferences, *operators.CLASSES)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    keymaps.register()


def unregister():
    operators.cancel_active()
    keymaps.unregister()
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
