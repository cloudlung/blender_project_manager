bl_info = {
    "name": "Ballz",
    "author": "Ballzstien",
    "version": (1, 2),
    "blender": (4, 5, 0),  # you're on 4.5
    "location": "View3D > Sidebar > BallzTools",
    "description": "Project Manager",
    "warning": "",
    "doc_url": "http://www.iogottlich.com",
    "category": "Development",
}

import os
import re
import bpy
from bpy.app.handlers import persistent

# --------------------------
# Helpers for dynamic enums
# --------------------------

def _safe_listdir(path):
    try:
        return sorted([d for d in os.listdir(path)])
    except Exception:
        return []

def _dir_items(root):
    return [(d, d, "") for d in _safe_listdir(root) if os.path.isdir(os.path.join(root, d))]

def _blend_items(path):
    return [(f, f, "") for f in _safe_listdir(path) if f.endswith(".blend")]

# Dynamic items callbacks
def get_project_items(self, context):
    root = context.scene.my_root_path
    if os.path.isdir(root):
        items = _dir_items(root)
        return items or [("","<no projects>","")]
    return [("","<root not found>","")]

def get_asset_or_shot_items(self, context):
    root = context.scene.my_root_path
    project = context.scene.project_list
    kind = context.scene.asset_or_shot  # 'Asset' or 'Shot'
    base = os.path.join(root, project, "01_Data", "01_Blender", kind)
    if os.path.isdir(base):
        items = _dir_items(base)
        return items or [("","<empty>","")]
    return [("","<path missing>","")]

def get_blend_file_items(self, context):
    root = context.scene.my_root_path
    project = context.scene.project_list
    kind = context.scene.asset_or_shot
    subdir = context.scene.asset_or_shot_list
    base = os.path.join(root, project, "01_Data", "01_Blender", kind, subdir)
    if os.path.isdir(base):
        items = _blend_items(base)
        return items or [("","<no .blend files>","")]
    return [("","<path missing>","")]

# --------------------------
# Version bumping
# --------------------------

def change_version_number(filepath, increment_by=1):
    m = re.search(r"_v(\d+)", filepath)
    if not m:
        return filepath
    cur = int(m.group(1))
    new = cur + increment_by
    return re.sub(r"_v\d+", f"_v{new:02}", filepath)

class IncrementVersionNumberOperator(bpy.types.Operator):
    bl_idname = "ballz.increment_version_number"
    bl_label = "Increment Version Number"
    def execute(self, context):
        cur = bpy.data.filepath
        new = change_version_number(cur)
        bpy.ops.wm.save_as_mainfile(filepath=new)
        return {"FINISHED"}

# --------------------------
# Refresh hooks (lightweight)
# --------------------------

def refresh_project_list(self, context):
    # Nothing to do; Enum uses dynamic items.
    return None

def refresh_asset_or_shot_list(self, context):
    # Nothing to do; Enum uses dynamic items.
    return None

def refresh_blend_file_list(self, context):
    # Nothing to do; Enum uses dynamic items.
    return None

# --------------------------
# Operators
# --------------------------

class RefreshProjectsOperator(bpy.types.Operator):
    bl_idname = "ballz.refresh_projects"
    bl_label = "Refresh Projects"
    def execute(self, context):
        # Force UI redraw; items are dynamic anyway
        context.area.tag_redraw()
        return {"FINISHED"}

def create_project_folder(project_name, root_path):
    project_path = os.path.join(root_path, project_name)
    os.makedirs(project_path, exist_ok=True)

    dirs = [
        "00_Assets/Textures",
        "00_Assets/Models",
        "00_Assets/Audio",
        "00_Assets/Cache",
        "01_Data/00_Houdini/Bgeo",
        "01_Data/00_Houdini/Hip",
        "01_Data/01_Blender/",
        "01_Data/03_AfterEffects/Source",
        "01_Data/04_DavinciResolve/Source",
        "01_Data/06_SubstancePainter/Source",
        "02_Exports/Drafts",
        "02_Exports/Final",
        "02_Exports/Playblasts"
        "02_Exports/Previews"
        "03_Scripts",
        "04_Client",
    ]
    for d in dirs:
        os.makedirs(os.path.join(project_path, d), exist_ok=True)

    readme = os.path.join(project_path, "README.md")
    if not os.path.exists(readme):
        with open(readme, "w", encoding="utf-8") as f:
            f.write("# Project description and instructions\n")
    return project_path

class CreateProjectOperator(bpy.types.Operator):
    bl_idname = "ballz.create_project"
    bl_label = "Create Project"
    def execute(self, context):
        create_project_folder(context.scene.my_project_name, context.scene.my_root_path)
        context.area.tag_redraw()
        return {"FINISHED"}

class SaveAssetOrShotOperator(bpy.types.Operator):
    bl_idname = "ballz.save_asset_or_shot"
    bl_label = "Save Asset or Shot"
    def execute(self, context):
        root = context.scene.my_root_path
        project = context.scene.project_list or context.scene.my_project_name
        base = os.path.join(root, project, "01_Data", "01_Blender")
        kind = context.scene.asset_or_shot  # 'Asset' or 'Shot'
        dir_name = context.scene.dir_name or context.scene.asset_or_shot_name
        full_path = os.path.join(base, kind, dir_name)
        os.makedirs(full_path, exist_ok=True)
        blend_name = f"{context.scene.asset_or_shot_name or 'untitled'}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(full_path, blend_name))
        context.area.tag_redraw()
        return {"FINISHED"}

class LoadAssetOrShotOperator(bpy.types.Operator):
    bl_idname = "ballz.load_asset_or_shot"
    bl_label = "Load Asset or Shot"
    def execute(self, context):
        root = context.scene.my_root_path
        project = context.scene.project_list
        kind = context.scene.asset_or_shot
        sub = context.scene.asset_or_shot_list
        blend = context.scene.blend_file_list
        full = os.path.join(root, project, "01_Data", "01_Blender", kind, sub, blend)
        if os.path.exists(full):
            bpy.ops.wm.open_mainfile(filepath=full)
            return {"FINISHED"}
        self.report({"WARNING"}, f"No such file: {full}")
        return {"CANCELLED"}

class SetRenderPathOperator(bpy.types.Operator):
    bl_idname = "ballz.set_render_path"
    bl_label = "Set Render Path"
    def execute(self, context):
        root = context.scene.my_root_path
        project = context.scene.project_list or context.scene.my_project_name
        render_path = os.path.join(root, project, "Render")
        os.makedirs(render_path, exist_ok=True)
        context.scene.render.filepath = os.path.join(render_path, "")
        self.report({"INFO"}, f"Render path set to: {render_path}")
        return {"FINISHED"}

# --------------------------
# Panel
# --------------------------

class ProjectManagementPanel(bpy.types.Panel):
    bl_label = "Project Management"
    bl_idname = "BALLZ_PT_project_management"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BallzTools"
    def draw(self, context):
        layout = self.layout
        col = layout.column()

        # Project
        col.prop(context.scene, "my_project_name")
        col.prop(context.scene, "my_root_path")
        col.operator("ballz.create_project", icon="FILE_FOLDER")

        col.separator()
        col.label(text="Save Functions:")
        col.prop(context.scene, "project_list", text="Choose Project")
        col.prop(context.scene, "asset_or_shot")
        col.prop(context.scene, "asset_or_shot_name")
        col.prop(context.scene, "dir_name")
        col.operator("ballz.save_asset_or_shot", icon="FILE_TICK")

        col.separator()
        col.label(text="Load Functions:")
        col.prop(context.scene, "project_list", text="Choose Project")
        col.prop(context.scene, "asset_or_shot")
        col.prop(context.scene, "asset_or_shot_list", text="Choose Asset/Shot")
        col.prop(context.scene, "blend_file_list", text="Choose Blend File")
        col.operator("ballz.load_asset_or_shot", icon="FILEBROWSER")

        col.separator()
        col.label(text="Refresh:")
        col.operator("ballz.refresh_projects", icon="FILE_REFRESH")

        col.separator()
        col.label(text="Render Functions:")
        col.operator("ballz.set_render_path", icon="RENDER_STILL")

        col.separator()
        col.label(text="Version Control:")
        col.operator("ballz.increment_version_number", icon="SORTSIZE")

# --------------------------
# Handlers & Props
# --------------------------

@persistent
def load_handler(_):
    # Items are dynamic; handler just nudges UI to update after file load.
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            area.tag_redraw()

def register_props():
    # NOTE: use forward slashes to avoid backslash escapes on Windows
    bpy.types.Scene.my_project_name = bpy.props.StringProperty(
        name="Project Name",
        default="MyProject",
        update=refresh_project_list,
    )
    bpy.types.Scene.my_root_path = bpy.props.StringProperty(
        name="Root Path",
         default="/media/cloud/Projects1/01_Projects/",  # <-- fixed (no raw-string-with-trailing-backslash) CHANGE LOCATION HERE  <----<-----<-----
        subtype='DIR_PATH',
        update=refresh_project_list,
    )
    bpy.types.Scene.asset_or_shot = bpy.props.EnumProperty(
        items=[('Asset', 'Asset', ''), ('Shot', 'Shot', '')],
        name="Asset or Shot",
        default='Asset',
        update=refresh_asset_or_shot_list,
    )
    bpy.types.Scene.asset_or_shot_name = bpy.props.StringProperty(name="Name", default="")
    bpy.types.Scene.dir_name = bpy.props.StringProperty(name="Directory Name", default="")

    # Dynamic enums (items callbacks)
    bpy.types.Scene.project_list = bpy.props.EnumProperty(
        name="Project List",
        description="List of available projects",
        items=get_project_items,
        update=refresh_asset_or_shot_list,
    )
    bpy.types.Scene.asset_or_shot_list = bpy.props.EnumProperty(
        name="Asset/Shot List",
        description="List of available assets or shots",
        items=get_asset_or_shot_items,
        update=refresh_blend_file_list,
    )
    bpy.types.Scene.blend_file_list = bpy.props.EnumProperty(
        name="Blend File List",
        description="List of available .blend files",
        items=get_blend_file_items,
    )

classes = (
    CreateProjectOperator,
    SaveAssetOrShotOperator,
    LoadAssetOrShotOperator,
    SetRenderPathOperator,
    ProjectManagementPanel,
    RefreshProjectsOperator,
    IncrementVersionNumberOperator,
)

def register():
    register_props()
    for c in classes:
        bpy.utils.register_class(c)
    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)

def unregister():
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    # Clean up props
    del bpy.types.Scene.my_project_name
    del bpy.types.Scene.my_root_path
    del bpy.types.Scene.asset_or_


