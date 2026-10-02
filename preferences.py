# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty

from . import keymaps

ADDON_ID = __package__


def get_preferences(context):
    addon = context.preferences.addons.get(ADDON_ID)
    return addon.preferences if addon else None


class QCW_Preferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_ID

    sensitivity: FloatProperty(
        name="Mouse Sensitivity", description="Value change per pixel of mouse movement", default=0.005,
        min=0.0001, max=0.1, precision=4,
    )
    show_hud: BoolProperty(name="Show HUD", default=True)
    hud_anchor: EnumProperty(name="Position", items=(
        ("BOTTOM", "Viewport Bottom", "Center at the bottom of the viewport"),
        ("TOP", "Viewport Top", "Center at the top of the viewport"),
        ("CURSOR", "Follow Mouse", "Display next to the mouse cursor"),
    ), default="BOTTOM")
    hud_offset_x: IntProperty(name="Horizontal Offset", default=0, min=-2000, max=2000)
    hud_offset_y: IntProperty(name="Vertical Offset", default=60, min=-2000, max=2000)
    hud_font_size: IntProperty(name="Value Font Size", default=38, min=12, max=96)
    hud_corner_radius: IntProperty(name="Corner Radius", description="Card corner radius; 0 for square corners", default=16, min=0, max=32)
    hud_panel_shadow: BoolProperty(name="Card Shadow", default=True)
    hud_text_color: FloatVectorProperty(name="Text Color", subtype="COLOR", size=4,
                                       default=(0.84, 0.88, 0.95, 1.0), min=0.0, max=1.0)
    hud_crease_color: FloatVectorProperty(name="Crease Theme Color", subtype="COLOR", size=4,
                                         default=(1.0, 0.5, 0.15, 1.0), min=0.0, max=1.0)
    hud_bevel_color: FloatVectorProperty(name="Bevel Weight Theme Color", subtype="COLOR", size=4,
                                        default=(0.25, 0.75, 1.0, 1.0), min=0.0, max=1.0)
    hud_background: BoolProperty(name="Show Background", default=True)
    hud_background_color: FloatVectorProperty(name="Background Color and Opacity", subtype="COLOR", size=4,
                                             default=(0.022, 0.029, 0.043, 0.94), min=0.0, max=1.0)
    hud_shadow: BoolProperty(name="Text Shadow", default=False)
    hud_show_help: BoolProperty(name="Show Right-hand Shortcut List", description="Keep a separate floating shortcut list to the right of the value HUD while adjusting", default=True)
    hud_show_bar: BoolProperty(name="Show Value Progress Bar", default=True)

    def draw(self, context):
        self.draw_settings(self.layout, context)

    def draw_settings(self, layout, context):
        layout.label(text="Mesh Edit Mode: vertex mode affects vertices; edge/face modes affect edges.")
        layout.label(text="Shortcuts", icon="KEYINGSET")
        keymaps.draw(layout, context)
        layout.prop(self, "sensitivity")
        box = layout.box()
        box.prop(self, "show_hud")
        column = box.column()
        column.enabled = self.show_hud
        column.use_property_split = True
        for name in ("hud_anchor", "hud_offset_x", "hud_offset_y", "hud_font_size", "hud_corner_radius",
                     "hud_text_color", "hud_crease_color", "hud_bevel_color", "hud_background"):
            column.prop(self, name)
        row = column.row()
        row.enabled = self.hud_background
        row.prop(self, "hud_background_color")
        row = column.row()
        row.enabled = self.hud_background
        row.prop(self, "hud_panel_shadow")
        for name in ("hud_shadow", "hud_show_help", "hud_show_bar"):
            column.prop(self, name)
        layout.label(text="LMB/Enter: confirm; RMB/Esc: restore; Shift: snap 0.1; Ctrl=1; Alt=0.")
        layout.label(text="Release the shortcut modifiers, then press them again to use these controls.")
        layout.label(text="Shortcuts and HUD settings are saved with Blender preferences.", icon="INFO")
