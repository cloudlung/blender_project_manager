bl_info = {
    "name": "Ballz",
    "author": "Ballzstien",
    "version": (1, 1),
    "blender": (3, 65, 0),
    "location": "View3D > Tool Shelf",
    "description": "Project Manager",
    "warning": "",
    "doc_url": "http://www.iogottlich.com",
    "category": "Development",
}

import os
import re
import bpy
from bpy.app.handlers import persistent

# Add the persistent decorator
@persistent  
def load_handler(dummy):
    print("Inside load_handler")  # Debugging line
    refresh_project_list(None, bpy.context)
    refresh_asset_or_shot_list(None, bpy.context)
    
# Function for changing version number
def change_version_number(filepath, increment_by=1):
    match = re.search(r'_v(\d+)', filepath)
    if match:
        current_version = int(match.group(1))
        new_version = current_version + increment_by
        new_filepath = re.sub(r'_v\d+', f'_v{new_version:02}', filepath)
        return new_filepath
    else:
        return filepath
    
# Function for incrementing version numbers
class IncrementVersionNumberOperator(bpy.types.Operator):
    bl_idname = "object.increment_version_number"
    bl_label = "Increment Version Number"

    def execute(self, context):
        current_file_path = bpy.data.filepath
        new_file_path = change_version_number(current_file_path)
        bpy.ops.wm.save_as_mainfile(filepath=new_file_path)
        return {'FINISHED'}

# Refresh and Populate Choose Project list
def refresh_project_list(self, context):
    print("Inside refresh_project_list")
    root_path = context.scene.my_root_path
    if os.path.exists(root_path):
        print(f"Root path is: {root_path}")  # Debugging line
        projects = [(d, d, '') for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
        bpy.types.Scene.project_list = bpy.props.EnumProperty(
            items=projects,
            name="Project List",
            description="List of available projects",
        )
    else:
        # debug line
        print(f"Could not find root_path: {root_path}")
        
# Function to refresh and populate Choose Asset/Shot list
def refresh_asset_or_shot_list(self, context):
    print("Inside refresh_asset_or_shot_list")
    root_path = context.scene.my_root_path
    project_name = context.scene.project_list
    asset_or_shot = context.scene.asset_or_shot
    asset_or_shot_path = os.path.join(root_path, project_name, "01_Data", "01_Blender", asset_or_shot)
    
    if os.path.exists(asset_or_shot_path):
        asset_or_shots = [(d, d, '') for d in os.listdir(asset_or_shot_path) if os.path.isdir(os.path.join(asset_or_shot_path, d))]
        bpy.types.Scene.asset_or_shot_list = bpy.props.EnumProperty(
            items=asset_or_shots,
            name="Asset/Shot List",
            description="List of available assets or shots",
            update=refresh_blend_file_list  # <-- update the blend file list whenever this changes
        )
    else:
        print(f"Could not find asset_or_shot_path: {asset_or_shot_path}")
        
        #RefreshProjectsOperator class
class RefreshProjectsOperator(bpy.types.Operator):
    bl_idname = "object.refresh_projects"
    bl_label = "Refresh Projects"
    
    def execute(self, context):
        refresh_project_list(None, context)
        return {'FINISHED'}

# Function to create project folder and its sub-folders
def create_project_folder(project_name, root_path):
    print("Inside create_project_folder")  # Debugging line
    project_path = os.path.join(root_path, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)

    dirs = [
        '00_Assets/Textures',
        '00_Assets/Models',
        '00_Assets/Audio',
        '00_Assets/Cache',
        '01_Data/00_Houdini/Bgeo',
        '01_Data/00_Houdini/Hip',
        '01_Data/01_Blender/',
        '01_Data/03_AfterEffects/Source',
        '01_Data/04_DavinciResolve/Source',
        '02_Exports/Drafts',
        '02_Exports/Final',
        '03_Scripts',
        '04_Client',
    ]

    for d in dirs:
        os.makedirs(os.path.join(project_path, d))

    with open(os.path.join(project_path, 'README.md'), 'w') as f:
        f.write("# Project description and instructions")

    return project_path

# Function to refresh and populate .blend files in the selected Asset/Shot directory
def refresh_blend_file_list(self, context):
    print("Inside refresh_blend_file_list")
    root_path = context.scene.my_root_path
    project_name = context.scene.project_list
    asset_or_shot = context.scene.asset_or_shot
    selected_dir = context.scene.asset_or_shot_list
    selected_dir_path = os.path.join(root_path, project_name, "01_Data", "01_Blender", asset_or_shot, selected_dir)
    
    if os.path.exists(selected_dir_path):
        blend_files = [(f, f, '') for f in os.listdir(selected_dir_path) if f.endswith('.blend')]
        bpy.types.Scene.blend_file_list = bpy.props.EnumProperty(
            items=blend_files,
            name="Blend File List",
            description="List of available .blend files",
        )
    else:
        print(f"Could not find selected_dir_path: {selected_dir_path}")
        
# Register properties to the active scene for UI editing
def register_props():
    bpy.types.Scene.my_project_name = bpy.props.StringProperty(name="Project Name", default="MyProject", update=refresh_project_list)
    bpy.types.Scene.my_root_path = bpy.props.StringProperty(name="Root Path", default="D:\\_Projects_", update=refresh_project_list)
    bpy.types.Scene.asset_or_shot = bpy.props.EnumProperty(items=[('Asset', 'Asset', ''), ('Shot', 'Shot', '')], name="Asset or Shot", default='Asset', update=refresh_asset_or_shot_list)
    bpy.types.Scene.asset_or_shot_name = bpy.props.StringProperty(name="Name", default="")
    bpy.types.Scene.dir_name = bpy.props.StringProperty(name="Directory Name", default="")
    bpy.types.Scene.project_list = bpy.props.EnumProperty(
        items=[],
        name="Project List",
        description="List of available projects",
        update=refresh_asset_or_shot_list  # Add this line
    )
    bpy.types.Scene.asset_or_shot_list = bpy.props.EnumProperty(
        items=[],
        name="Asset/Shot List",
        description="List of available assets or shots",
    )  # Blend file
    bpy.types.Scene.blend_file_list = bpy.props.EnumProperty(
        items=[],
        name="Blend File List",
        description="List of available .blend files",
    ) 
# Blender Operator to create a project
class CreateProjectOperator(bpy.types.Operator):
    bl_idname = "object.create_project"
    bl_label = "Create Project"
    
    def execute(self, context):
        print("Inside execute of CreateProjectOperator")                                            # Debugging line
        create_project_folder(context.scene.my_project_name, context.scene.my_root_path)
        refresh_project_list(self, context)
        return {'FINISHED'}

# Blender Operator to save an asset or shot
class SaveAssetOrShotOperator(bpy.types.Operator):
    bl_idname = "object.save_asset_or_shot"
    bl_label = "Save Asset or Shot"
    
    def execute(self, context):
        print("Inside execute of SaveAssetOrShotOperator")                                          # Debugging line
        base_path = os.path.join(context.scene.my_root_path, context.scene.my_project_name, "01_Data", "01_Blender")
        asset_or_shot = context.scene.asset_or_shot
        dir_name = context.scene.dir_name if context.scene.dir_name else context.scene.asset_or_shot_name
        full_path = os.path.join(base_path, asset_or_shot, dir_name)
        refresh_asset_or_shot_list(self, context)  # Add this line to refresh the asset_or_shot_list
       
       
        if not os.path.exists(full_path):
            os.makedirs(full_path)

        blend_file_name = f"{context.scene.asset_or_shot_name}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(full_path, blend_file_name))
        return {'FINISHED'}

# Blender Operator to load an asset or shot
class LoadAssetOrShotOperator(bpy.types.Operator):
    bl_idname = "object.load_asset_or_shot"
    bl_label = "Load Asset or Shot"

    def execute(self, context):
        print("Inside execute of LoadAssetOrShotOperator")
        base_path = os.path.join(context.scene.my_root_path, context.scene.project_list, "01_Data", "01_Blender")
        asset_or_shot = context.scene.asset_or_shot
        selected_dir = context.scene.asset_or_shot_list  # Directory name
        selected_blend_file = context.scene.blend_file_list  # Selected .blend file name
        full_path = os.path.join(base_path, asset_or_shot, selected_dir, selected_blend_file)  # Added selected_blend_file

        if os.path.exists(full_path):
            bpy.ops.wm.open_mainfile(filepath=full_path)
        else:
            self.report({'WARNING'}, f"No such file: {full_path}")

        return {'FINISHED'}

    
# SetRenderPathOperator class
class SetRenderPathOperator(bpy.types.Operator):
    bl_idname = "object.set_render_path"
    bl_label = "Set Render Path"
    
    def execute(self, context):
        render_folder = "Render"
        base_path = os.path.join(context.scene.my_root_path, context.scene.my_project_name)
        render_path = os.path.join(base_path, render_folder)
        
        if not os.path.exists(render_path):
            os.makedirs(render_path)
        
        bpy.context.scene.render.filepath = os.path.join(render_path, "")
        self.report({'INFO'}, f"Render path set to: {render_path}")
        return {'FINISHED'}

# Blender UI Panel
class ProjectManagementPanel(bpy.types.Panel):
    bl_label = "Project Management"
    bl_idname = "PT_ProjectManagementPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BallzTools'
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
# Project button
        col.prop(context.scene, "my_project_name")
        col.prop(context.scene, "my_root_path")
        col.operator("object.create_project")
# Save Button
        col.separator()
        col.label(text="Save Functions:")
        col.prop(context.scene, "asset_or_shot")
        col.prop(context.scene, "asset_or_shot_name")
        col.prop(context.scene, "dir_name")
        col.operator("object.save_asset_or_shot")
# Load Button
        col.separator()
        col.label(text="Load Functions:")
        col.prop(context.scene, "project_list", text="Choose Project")
        col.prop(context.scene, "asset_or_shot")
        col.prop(context.scene, "asset_or_shot_list", text="Choose Asset/Shot")  
        col.prop(context.scene, "blend_file_list", text="Choose Blend File")
        col.operator("object.load_asset_or_shot")
        
# Refresh button
        col.separator()
        col.label(text="Refresh:")
        col.operator("object.refresh_projects")

# Button for SetRenderPathOperator
        col.separator()
        col.label(text="Render Functions:")
        col.operator("object.set_render_path")
        
# Button for Increment Version Number
        col.separator()
        col.label(text="Version Control:")
        col.operator("object.increment_version_number")

# Register classes and properties
def register():
    print("Inside register function")
    register_props()
    bpy.utils.register_class(CreateProjectOperator)
    bpy.utils.register_class(SaveAssetOrShotOperator)
    bpy.utils.register_class(LoadAssetOrShotOperator)
    bpy.utils.register_class(SetRenderPathOperator)
    bpy.utils.register_class(ProjectManagementPanel)
    bpy.app.handlers.load_post.append(load_handler)
    bpy.utils.register_class(RefreshProjectsOperator)
    bpy.utils.register_class(IncrementVersionNumberOperator)  

# Unregister classes and properties
def unregister():
    bpy.utils.unregister_class(CreateProjectOperator)
    bpy.utils.unregister_class(SaveAssetOrShotOperator)
    bpy.utils.unregister_class(LoadAssetOrShotOperator)
    bpy.utils.unregister_class(SetRenderPathOperator)  # Unregister the new operator
    bpy.utils.unregister_class(ProjectManagementPanel)
    bpy.utils.unregister_class(RefreshProjectsOperator)
    bpy.utils.unregister_class(IncrementVersionNumberOperator) 
    del bpy.types.Scene.my_project_name
    del bpy.types.Scene.my_root_path
    del bpy.types.Scene.asset_or_shot
    del bpy.types.Scene.asset_or_shot_name
    del bpy.types.Scene.dir_name
    del bpy.types.Scene.project_list
    del bpy.types.Scene.asset_or_shot_list

if __name__ == "__main__":
    register()
