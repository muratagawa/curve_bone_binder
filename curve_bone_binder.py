import bpy
from mathutils import Vector
import dataclasses


class CBB_OT_bind(bpy.types.Operator):
    bl_idname = "object.cbb_bind"
    bl_label = "Bind"
    bl_description = "Bind selected curve points to bones."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not bind_bones(context):
            return {'CANCELLED'}

        return {'FINISHED'}


@dataclasses.dataclass
class CurveBoneTable:
    point: bpy.types.SplinePoint
    coordinate: Vector
    bone_name: str = ""


# Show in Hook (Ctrl+H) context menu
def show_in_hook(self, context):
    self.layout.operator(CBB_OT_bind.bl_idname, text="Hook to new bones")


# Popup message box
def popup_message_box(message="", title="", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# Store corrdinates of selected curve points
def get_curve_points_list(curve):
    point_list = []

    for spline in curve.data.splines:
        if spline.type == 'BEZIER':
            for point in spline.bezier_points:
                if point.select_control_point:
                    point_list.append(CurveBoneTable(point, point.co))
        elif spline.type == 'POLY' or spline.type == 'NURBS':
            for point in spline.points:
                if point.select:
                    point_list.append(CurveBoneTable(point, point.co))

    return point_list


# Bind the selected control points to the new bones.
def bind_bones(context):
    if (not context.active_object
            or len(context.selected_objects) != 2):
        popup_message_box(
            "Select an armature object and a curve object.", "Error", 'ERROR')
        return False

    # Get armature and curve objects
    armature = None
    curve = None

    for obj in context.selected_objects:
        if obj.type == 'ARMATURE':
            armature = obj
        elif obj.type == 'CURVE':
            curve = obj

    if not armature or not curve:
        popup_message_box(
            "Select an armature object and a curve object.", "Error", 'ERROR')
        return False

    points_list = get_curve_points_list(curve)
    if not points_list:
        popup_message_box("Select at least one curve point.", "Error", 'ERROR')
        return False

    # Add bones to the armature
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    for item in points_list:
        # Because curve points are in local coordinates, we need to convert them to world space (matrix_world)
        wm_offset = curve.matrix_world @ item.coordinate
        bone = armature.data.edit_bones.new(name="HookBone")
        bone.head = wm_offset
        bone.tail = wm_offset + Vector((0, 0, 0.5))
        item.bone_name = bone.name

    # Add Hook modifier and assign the curve points to the bones
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = curve
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.curve.select_all(action='DESELECT')

    for item in points_list:
        item.point.select_control_point = True
        mod = curve.modifiers.new(name="Hook", type='HOOK')
        mod.object = armature
        mod.subtarget = item.bone_name
        bpy.ops.object.hook_assign(modifier=mod.name)
        item.point.select_control_point = False

    bpy.ops.object.mode_set(mode='OBJECT')
    return True


def register_curve_bone_binder():
    bpy.utils.register_class(CBB_OT_bind)
    bpy.types.VIEW3D_MT_hook.append(show_in_hook)


def unregister_curve_bone_binder():
    bpy.utils.unregister_class(CBB_OT_bind)
    bpy.types.VIEW3D_MT_hook.remove(show_in_hook)


if __name__ == "__main__":
    register_curve_bone_binder()
