import bpy
from mathutils import Vector
import dataclasses


class CBB_OT_bind(bpy.types.Operator):
    bl_idname = "object.cbb_bind"
    bl_label = "Bind"
    bl_description = "Bind selected curve points to new bones."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not bind_bones(self, context):
            return {'CANCELLED'}

        return {'FINISHED'}


@dataclasses.dataclass
class CurveBoneTable:
    point_index: int
    spline_index: int
    type: str
    coordinate: Vector


# Show in Hooks menu
def show_in_menu(self, context):
    self.layout.operator(CBB_OT_bind.bl_idname, text="Hook to new bones")


# Popup message box
def popup_message_box(message="", title="", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# Store corrdinates of selected curve points
def get_curve_points_list(curve):
    point_list = []

    for s_idx, spline in enumerate(curve.data.splines):
        if spline.type == 'BEZIER':
            for p_idx, point in enumerate(spline.bezier_points):
                if point.select_control_point:
                    point_list.append(CurveBoneTable(
                        p_idx, s_idx, spline.type, point.co))
        elif spline.type == 'POLY' or spline.type == 'NURBS':
            for p_idx, point in enumerate(spline.points):
                if point.select:
                    point_list.append(CurveBoneTable(
                        p_idx, s_idx, spline.type, point.co))

    return point_list


def deselect_all_curve_points(curve_object):
    for spline in curve_object.data.splines:
        if spline.type == 'BEZIER':
            for point in spline.bezier_points:
                point.select_control_point = False
                point.select_right_handle = False
                point.select_left_handle = False
        elif spline.type == 'POLY' or spline.type == 'NURBS':
            for point in spline.points:
                point.select = False


def deselect_all_bones(armature):
    for bone in armature.data.bones:
        bone.select = False


def switch_mode(mode):
    bpy.ops.object.mode_set(mode=mode)


# Bind the selected control points to the new bones.
def bind_bones(self, context) -> bool:
    # !!IMPORTANT!! Mesh/curve data is not synchronized in Edit mode.
    # So you must switch to Object mode to access the latest data before operation.
    # ref: https://docs.blender.org/api/current/info_gotcha.html#modes-and-mesh-access
    switch_mode('OBJECT')

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

    for item in points_list:
        # Translate local coordinate of the curve point to world coordinate
        target_world_co = curve.matrix_world @ item.coordinate

        # Translate world coordinate to Armature space local coordinate
        target_armature_local_co = armature.matrix_world.inverted() @ target_world_co
        bpy.context.scene.cursor.location = target_world_co

        # Add bone
        switch_mode('OBJECT')
        bpy.context.view_layer.objects.active = armature
        switch_mode('EDIT')

        bone = armature.data.edit_bones.new(name="HookBone")
        bone.head = target_armature_local_co
        bone.tail = target_armature_local_co + Vector((0, 0, 1))
        bone_name = bone.name

        # Select the added bone in pose mode
        switch_mode('POSE')
        deselect_all_bones(armature)
        armature.data.bones[bone_name].select = True

        # Add Hook modifier and assign the curve points to the bones
        switch_mode('OBJECT')
        curve.select_set(True)
        bpy.context.view_layer.objects.active = curve
        switch_mode('EDIT')
        deselect_all_curve_points(curve)

        mod = curve.modifiers.new(name="Hook", type='HOOK')
        mod.object = armature
        mod.subtarget = bone_name
        curve.data.splines[item.spline_index].bezier_points[item.point_index].select_control_point = True
        curve.data.splines[item.spline_index].bezier_points[item.point_index].select_right_handle = True
        curve.data.splines[item.spline_index].bezier_points[item.point_index].select_left_handle = True
        bpy.ops.object.hook_assign(modifier=mod.name)
        self.report({'INFO'}, "Hook created. (Bone=" + bone_name + ", Modifier=" + mod.name + ")")

    switch_mode('OBJECT')
    return True


def register_curve_bone_binder():
    bpy.utils.register_class(CBB_OT_bind)
    bpy.types.VIEW3D_MT_hook.append(show_in_menu)


def unregister_curve_bone_binder():
    bpy.utils.unregister_class(CBB_OT_bind)
    bpy.types.VIEW3D_MT_hook.remove(show_in_menu)


if __name__ == "__main__":
    register_curve_bone_binder()
