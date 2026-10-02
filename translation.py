# SPDX-License-Identifier: GPL-3.0-or-later
"""Native Blender translations; resolve dynamic text at draw time."""
import bpy
from bpy.app.translations import pgettext_iface as tr, pgettext_rpt as rpt


ZH_CN = {
    "Quickly adjust vertex or edge creases and bevel weights with custom shortcuts and a HUD":
        "根据点/边选择模式快速调整折痕与倒角权重，支持自定义快捷键与 HUD",
    "Quick Crease": "快速折痕",
    "Quick Bevel Weight": "快速倒角权重",
    "Adjust vertex or edge creases based on the mesh selection mode": "按网格选择模式调整顶点或边折痕",
    "Adjust vertex or edge bevel weights based on the mesh selection mode": "按网格选择模式调整顶点或边倒角权重",
    "Crease": "折痕",
    "Bevel Weight": "倒角权重",
    "Mouse Sensitivity": "鼠标灵敏度",
    "Value change per pixel of mouse movement": "每移动一个像素调整的数值",
    "Show HUD": "显示 HUD",
    "Position": "位置",
    "Viewport Bottom": "视口底部",
    "Center at the bottom of the viewport": "固定在视口底部居中",
    "Viewport Top": "视口顶部",
    "Center at the top of the viewport": "固定在视口顶部居中",
    "Follow Mouse": "跟随鼠标",
    "Display next to the mouse cursor": "显示在鼠标旁边",
    "Horizontal Offset": "水平偏移",
    "Vertical Offset": "垂直偏移",
    "Value Font Size": "数值字号",
    "Corner Radius": "圆角半径",
    "Card corner radius; 0 for square corners": "卡片圆角大小，0 为直角",
    "Card Shadow": "卡片阴影",
    "Text Color": "文字颜色",
    "Crease Theme Color": "折痕主题色",
    "Bevel Weight Theme Color": "倒角权重主题色",
    "Show Background": "显示背景",
    "Background Color and Opacity": "背景颜色与透明度",
    "Text Shadow": "文字阴影",
    "Show Right-hand Shortcut List": "显示右侧按键列表",
    "Keep a separate floating shortcut list to the right of the value HUD while adjusting":
        "工具操作期间，在数值 HUD 右侧持续显示独立的悬浮操作列表",
    "Show Value Progress Bar": "显示数值进度条",
    "Mesh Edit Mode: vertex mode affects vertices; edge/face modes affect edges.":
        "网格编辑模式：点模式作用于顶点，边/面模式作用于边。",
    "Shortcuts": "快捷键",
    "LMB/Enter: confirm; RMB/Esc: restore; Shift: snap 0.1; Ctrl=1; Alt=0.":
        "左键/Enter 确认；右键/Esc 还原；Shift 吸附 0.1；Ctrl=1；Alt=0。",
    "Release the shortcut modifiers, then press them again to use these controls.":
        "调用快捷键后，先松开修饰键，再按下即可使用上述控制。",
    "Shortcuts and HUD settings are saved with Blender preferences.": "快捷键和 HUD 设置随 Blender 偏好设置保存。",
    "Shortcuts will appear after Blender updates its key configuration": "快捷键将在 Blender 更新键位配置后显示",
    "Mouse": "鼠标",
    "Drag left/right": "左右拖动",
    "Snap 0.1": "吸附 0.1",
    "Set to 1": "设为 1",
    "Set to 0": "设为 0",
    "Confirm": "确认",
    "Cancel": "取消",
    "Vertices": "顶点",
    "Edges": "边",
    "{tool} | LMB/Enter: confirm | RMB/Esc: restore | Shift: snap 0.1 | Ctrl=1 | Alt=0":
        "{tool} | 左键/Enter 确认 | 右键/Esc 还原 | Shift 吸附 0.1 | Ctrl=1 | Alt=0",
    "Run this tool in a 3D viewport": "请在 3D 视口内调用",
    "Unsupported attribute or mesh domain": "不支持的属性或网格域",
    "{object}: {attribute} already exists but is not a float attribute on the correct domain":
        "{object}: {attribute} 已存在，但不是正确域的浮点属性",
    "Select vertices or edges first": "请先选择顶点或边",
    "The mesh has left Edit Mode": "网格已离开编辑模式",
}

# RNA labels use the default context; operator names use Operator.
_messages = {(context, source): target
             for context in (bpy.app.translations.contexts.default,
                             bpy.app.translations.contexts.operator_default)
             for source, target in ZH_CN.items()}
TRANSLATIONS = {locale: _messages for locale in ("zh_HANS", "zh_CN")}


def register():
    bpy.app.translations.register(__name__, TRANSLATIONS)


def unregister():
    bpy.app.translations.unregister(__name__)
