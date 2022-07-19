bl_info = {
    "name": "Curve Bone Binder",
    "author": "Kei Muratagawa",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D Edit mode: Menubar > Control Points > Hooks (Ctrl+H)",
    "description": "Bind bones to selected curve points",
    "doc_url": "https://github.com/muratagawa/curve_bone_binder",
    "category": "Edit",
}

# Load local python script (reload if already imported)
if "bpy" in locals():
    import importlib
    importlib.reload(curve_bone_binder)


def register():
    from .curve_bone_binder import register_curve_bone_binder
    register_curve_bone_binder()


def unregister():
    from .curve_bone_binder import unregister_curve_bone_binder
    unregister_curve_bone_binder()
