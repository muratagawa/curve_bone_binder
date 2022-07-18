import bpy
from mathutils import Vector


class CBB_OT_bind(bpy.types.Operator):
    bl_idname = "object.cbb_bind"
    bl_label = "Bind"
    bl_description = "Bind selected curve points to bones."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not bind_bones(context):
            return {'CANCELLED'}

        return {'FINISHED'}


# Popup message box
def popup_message_box(message="", title="", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# Store corrdinates of selected curve points
def get_curve_points_coordinates(curve):
    coordinates = []

    for spline in curve.data.splines:
        if spline.type == 'BEZIER':
            for point in spline.bezier_points:
                if point.select_control_point:
                    coordinates.append(point.co)
        elif spline.type == 'POLY' or spline.type == 'NURBS':
            for point in spline.points:
                if point.select:
                    coordinates.append(point.co)

    return coordinates


# Add bones to the selected armature at the coordinates of the curve points
def bind_bones(context):
    if not context.active_object:
        popup_message_box("Select an armature object.", "Error", 'ERROR')
        return False

    if len(context.selected_objects) != 2:
        popup_message_box("Select an armature and a curve object.", "Error", 'ERROR')
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
        popup_message_box("Select an armature and a curve object.", "Error", 'ERROR')
        return False

    coodinates = get_curve_points_coordinates(curve)
    if not coodinates:
        popup_message_box("No curve point selected", "Error", 'ERROR')
        return False

    # Add bones to the armature
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    for coordinate in coodinates:
        # Because curve points are in local coordinates, we need to convert them to world space (matrix_world)
        wm_offset = curve.matrix_world @ coordinate
        bone = armature.data.edit_bones.new(name="HookBone")
        bone.head = wm_offset
        bone.tail = wm_offset + Vector((0, 0, 0.5))

    # TODO Add Hook modifier to curve object to the bones

    return True


def register_curve_bone_binder():
    bpy.utils.register_class(CBB_OT_bind)


def unregister_curve_bone_binder():
    bpy.utils.unregister_class(CBB_OT_bind)


if __name__ == "__main__":
    register_curve_bone_binder()
