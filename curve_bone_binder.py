import bpy


class CBB_OT_bind(bpy.types.Operator):
    bl_idname = "object.cbb_bind"
    bl_label = "Bind"
    bl_description = "Bind selected curve points to bones."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bind_bones(context)
        return {'FINISHED'}


# Popup message box
def popup_message_box(message="", title="", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# Check if any curve point is selected
def is_curve_point_selected():
    for obj in bpy.context.selected_objects:
        if obj.type == 'CURVE':
            for spline in obj.data.splines:
                for point in spline.points:
                    if point.select_control_point:
                        return True
    return False


# Add a bone to selected curve points
def bind_bones(context):
    # Error if no curve point is selected
    if not is_curve_point_selected():
        popup_message_box("No curve point selected", "Error", 'ERROR')
        return

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.bone_primitive_add()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set bone name to selected curve points
    for obj in bpy.context.selected_objects:
        if obj.type == 'CURVE':
            for spline in obj.data.splines:
                for point in spline.points:
                    if point.select_control_point:
                        obj.data.edit_bones[-1].name = point.name
                        break

    # Set bone parent to selected curve points
    for obj in bpy.context.selected_objects:
        if obj.type == 'CURVE':
            for spline in obj.data.splines:
                for point in spline.points:
                    if point.select_control_point:
                        obj.data.edit_bones[-1].parent = obj.data.edit_bones[point.name]
                        break


def register():
    bpy.utils.register_class(CBB_OT_bind)


def unregister():
    bpy.utils.unregister_class(CBB_OT_bind)


if __name__ == "__main__":
    register()

    # test call
    # bind_bones(bpy.context)
