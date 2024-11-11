#-------------------------------------------------------------------------------
#                     Extra Material List - Addon for Blender
#
# - Two display options (preview and plain list)
# - Display object and world materials
# - Eliminate duplicates for node groups and materials
#
# Version: 0.2
# Revised: 11.08.2017
# Author: Miki (meshlogic)
#-------------------------------------------------------------------------------

'''
# Changelog


## [0.2.6] - 2024-11-08

### Removed

- Simple Updater, think about Blenders Extension Platform, easier method perhaps

### Fixed

- Poll issue texture preview > update nested image texture nodegroup
- Update not working for nested image texture > nodegroup

## []0.2.5] - 2022-06-13

### Fixed

-Texture panel not showing inside node group

## []0.2.2.4] - 2021-07-29

### Changed

# - Check for Bl version to show Heading or not

## [0.2.3] - 2024-11-06

### Fixed

- Issue texture preview not showing with nested image textures

### Added

- Simple updater check

## [0.2.2.5] - 2021-07-28

### Fixed

= Panel issue difference 2.83 and 290

## 2021-04-08

### Added

- Check if we are in shading mode, should not show in Compositor
- Better filter for what to show > later add lights and perhaps grease pencil?
  Still needs work though
- Added popup operator menu > easy for fullscreen workflow

### Changed 

- default slot menu > changed slot to show actual name of the slot
- Updated default rows & cols

## [0.2.2.4] - 2021-07-29  

### Changed

- Check for Bl version to show Heading or not

'''

bl_info = {
    "name": "Extra Material List",
    "author": "Miki (meshlogic) - Rombout (2.8 upgrade)",
    "category": "Node",
    "description": "An alternative object/world material list for Node Editor.",
    "location": "Node Editor > Tools > Material List",
    "version": (0, 2, 6),
    "blender": (2, 80, 0)
}

import bpy
import os
import rna_keymap_ui
from bpy.props import (
    EnumProperty, 
    StringProperty, 
    BoolProperty, 
    IntProperty, 
    PointerProperty
    )
from bpy.types import (
    Menu, 
    Operator, 
    Panel, 
    UIList, 
    AddonPreferences
)
from bpy.app.handlers import persistent
from . import registers

# See if we still want this with extension platform now being live
# from . import updater

#-------------------------------------------------------------------------------
# Material Popover Menu
#-------------------------------------------------------------------------------
# Adjust slot > to material name > make more sense
class EML_PT_material_slots(Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'HEADER'
    bl_label = "Slot"
    bl_ui_units_x = 12

    def draw_header(self, context):
        ob = context.object
        self.bl_label = (
            # "Slot " + str(ob.active_material_index + 1) if ob.material_slots else
            # "Slot"
            str(ob.active_material.name) if ob.material_slots else "Slot"
        )

    # Duplicate part of 'EEVEE_MATERIAL_PT_context_material'.
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()

        ob = context.object
        col.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index")

        col = row.column(align=True)
        col.operator("object.material_slot_add", icon='ADD', text="")
        col.operator("object.material_slot_remove", icon='REMOVE', text="")

        col.separator()

        col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

        if len(ob.material_slots) > 1:
            col.separator()

            col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if ob.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

#-------------------------------------------------------------------------------
# UI PANEL - Extra Material List
#-------------------------------------------------------------------------------
class EML_PT_Panel(Panel):
    bl_space_type  = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_label = "Extra Material List"

    #--- Available only for "shading nodes" render
    @classmethod
    def poll(cls, context):
        snode = context.space_data
        ob = context.active_object
        objs = {'MESH'}
        node_types = {'OBJECT','WORLD'}
        # print(ob.type)
        # if snode.shader_type in node_types:
        #     if ob.type in objs:
            # mat = ob.active_material.use_nodes
        return snode.tree_type == 'ShaderNodeTree' # mat and snode.node_tree is not None

    #--- Draw Panel
    def draw(self, context):
        layout = self.layout
        cs = context.scene
        ob = context.object
        sdata = context.space_data
        props = cs.extra_material_list

        #--- Shader tree and type selection
        row = layout.row()
        row.alignment = 'CENTER'
        # row.prop(sdata, "shader_type", text="", expand=True)
        row.prop(props, "shaderType",expand=True)

        #--- Proceed only for OBJECT/WORLD shader node trees
        if sdata.tree_type != 'ShaderNodeTree' or (sdata.shader_type != 'OBJECT' and sdata.shader_type != 'WORLD'):
            return

        #--- List style buttons
        row = layout.row()
        # row.prop(props, "style", expand=True)

        #-----------------------------------------------------------------------
        # PREVIEW Style
        #-----------------------------------------------------------------------
        if props.style == 'PREVIEW':

            #--- Object materials
            if sdata.shader_type == 'OBJECT':

                # List of all scene materials
                mat_list = bpy.data.materials

                # Current active material
                if hasattr(sdata.id_from, "active_material"):
                    mat = sdata.id_from.active_material
                else:
                    return
                
                layout.label(text=ob.name, icon='OUTLINER_OB_MESH')
                # From blender node_space
                if sdata.shader_type == 'OBJECT' and ob:
                    
                    types_that_support_material = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META',
                                                'GPENCIL', 'VOLUME', 'HAIR', 'POINTCLOUD'}
                    # disable material slot buttons when pinned, cannot find correct slot within id_from (T36589)
                    ob_type = ob.type
                    # disable also when the selected object does not support materials
                    has_material_slots = not sdata.pin and ob_type in types_that_support_material

                    if ob_type != 'LIGHT':
                        row = layout.row()
                        row.enabled = has_material_slots
                        row.ui_units_x = 4
                        if (bpy.app.version[1] < 90):
                            row = layout.column(align=True)
                            row.label(text="Material Slot")
                        else:
                            row = row.column(heading="Material Slot")
                        row.popover(panel="EML_PT_material_slots")
                        
                # Preview list
                ob = context.active_object
                objs = {'MESH'}
                sub = layout.row()
                sub.enabled = ob.type in objs # Disable when not mesh objects
                sub.template_ID_preview(
                    ob, "active_material", # changed to OB so we dont get greasepencil materials
                    new = "material.new",
                    rows = props.rows, cols = props.cols)

                row = layout.row()
                split = row.split(factor=0.5)

                # Navigation button PREV
                sub = split.column(align=True)
                sub.scale_y = 1.5
                sub.operator("extra_material_list.nav", text="", icon='BACK').dir = 'PREV'
                sub.enabled = enable_prev_button(mat, mat_list)

                # Navigation button NEXT
                sub = split.column(align=True)
                sub.scale_y = 1.5
                sub.operator("extra_material_list.nav", text="", icon='FORWARD').dir = 'NEXT'
                sub.enabled = enable_next_button(mat, mat_list)

                # Show Texture list if possible
                try:
                    # mNode = context.active_object.active_material.node_tree.nodes.active
                    if bpy.context.active_object.active_material:
                        mNode = bpy.context.active_object.active_material.node_tree.nodes.active
                        # print(mNode)
                        # print(mNode.type)
                        if mNode!=None:
                            if mNode.type=='GROUP':
                                mNode = mNode.node_tree.nodes.active
                        # print(mNode.type)
                        if mNode.type == 'TEX_IMAGE':
                            layout.label(text=mNode.name, icon='TEXTURE')
                            layout.template_ID_preview(
                            mNode, "image",
                            new = "image.new",
                            open = "image.open",
                            rows = props.rows, cols = props.cols)
                            img = mNode.image
                except:
                    pass

                #--- Get the current image in the UV editor and list of all images
                # img = context.space_data.image
                # img_list = bpy.data.images

            #--- World materials
            elif sdata.shader_type == 'WORLD':
                
                # List of all scene worlds
                world_list = bpy.data.worlds
                
                # Current active world
                world = context.scene.world
                
                # Preview list
                layout.template_ID_preview(
                    cs, "world",
                    new = "world.new",
                    rows = props.rows, cols = props.cols)

                row = layout.row()
                split = row.split(factor=0.5)
                
                # Navigation button PREV
                sub = split.column()
                sub.scale_y = 1.5
                sub.operator("extra_material_list.nav", text="", icon='BACK').dir = 'PREV'
                sub.enabled = enable_prev_button(world, world_list)
                
                # Navigation button NEXT
                sub = split.column()
                sub.scale_y = 1.5
                sub.operator("extra_material_list.nav", text="", icon='FORWARD').dir = 'NEXT'
                sub.enabled = enable_next_button(world, world_list)

                # Show Texture list if possible
                try:
                    wNode = world.node_tree.nodes.active
                    if wNode.type == 'TEX_ENVIRONMENT':
                        layout.label(text=wNode.name, icon='TEXTURE')
                        layout.template_ID_preview(
                        wNode, "image",
                        new = "image.new",
                        open = "image.open",
                        rows = props.rows, cols = props.cols)
                        img = wNode.image
                except:
                    pass


        # -----------------------------------------------------------------------
        # LIST Style
        # -----------------------------------------------------------------------
        elif props.style == 'LIST':

            #--- Object materials
            if sdata.shader_type == 'OBJECT':
                
                layout.label(text=ob.name, icon='OUTLINER_OB_MESH')

                # From blender node_space
                if sdata.shader_type == 'OBJECT' and ob:
                    types_that_support_material = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META',
                                            'GPENCIL', 'VOLUME', 'HAIR', 'POINTCLOUD'}
                    # disable material slot buttons when pinned, cannot find correct slot within id_from (T36589)
                    ob_type = ob.type
                    # disable also when the selected object does not support materials
                    has_material_slots = not sdata.pin and ob_type in types_that_support_material

                    if ob_type != 'LIGHT':
                        row = layout.row()
                        row.enabled = has_material_slots
                        row.ui_units_x = 4
                        if (bpy.app.version[1] < 90):
                            row = layout.column(align=True)
                            row.label(text="Material Slot")
                        else:
                            row = row.column(heading="Material Slot")
                        row.popover(panel="EML_PT_material_slots")

                layout.template_list(
                    "EML_UL_MaterialList", "",
                    bpy.data, "materials", #bpy.data
                    props, "material_id",
                    # rows = len(bpy.data.materials)
                )

                # Show Texture list if possible
                try:
                    # mNode = context.active_object.active_material.node_tree.nodes.active
                    if bpy.context.active_object.active_material:
                        mNode = bpy.context.active_object.active_material.node_tree.nodes.active
                        if mNode!=None:
                            if mNode.type=='GROUP':
                                mNode = mNode.node_tree.nodes.active
                    if mNode.type == 'TEX_IMAGE':
                        layout.label(text=mNode.name, icon='TEXTURE')
                        layout.template_ID_preview(
                        mNode, "image",
                        new = "image.new",
                        open = "image.open",
                        rows = props.rows, cols = props.cols)
                        img = mNode.image
                except:
                    pass

            #--- World materials
            elif sdata.shader_type == 'WORLD':

                # Current active world
                world = context.scene.world

                layout.template_list(
                    "EML_UL_MaterialList", "",
                    bpy.data, "worlds",
                    props, "world_id",
                    rows = len(bpy.data.worlds)
                )

                # Show Texture list if possible
                try:
                    wNode = world.node_tree.nodes.active
                    if wNode.type == 'TEX_ENVIRONMENT':
                        layout.label(text=wNode.name, icon='TEXTURE')
                        layout.template_ID_preview(
                        wNode, "image",
                        new = "image.new",
                        open = "image.open",
                        rows = props.rows, cols = props.cols)
                        img = wNode.image
                except:
                    pass


        #-----------------------------------------------------------------------
        # Image Source
        #-----------------------------------------------------------------------
        try:
            row = layout.row()
            if img != None:
                if props.info:
                    #--- Image source
                    row.prop(img, "source")
                    #row.label(text="Image Source:", icon='DISK_DRIVE')
                    row = layout.row(align=True)

                    if img.source == 'FILE':
                        if img.packed_file:
                            row.operator("image.unpack", text="", icon='PACKAGE')
                        else:
                            row.operator("image.pack", text="", icon='UGLYPACKAGE')

                        row.prop(img, "filepath", text="")
                        row.operator("image.reload", text="", icon='FILE_REFRESH')
                    else:
                        row.label(text=img.source + " : " + img.type)

                    #--- Image size
                    col = layout.column(align=True)
                    row = layout.row(align=True)
                    row.alignment = 'LEFT'

                    if img.has_data:
                        filename = os.path.basename(img.filepath)
                        #--- Image name
                        col.label(text=filename, icon='FILE_IMAGE')
                        #--- Image size
                        row.label(text="Size:", icon='TEXTURE')
                        row.label(text="%d x %d x %db" % (img.size[0], img.size[1], img.depth))
                    else:
                        row.label(text="Can't load image file!", icon='ERROR')
        except:
            pass

        # Disable button for the last image or for no images
        # sub.enabled = (img!=img_list[-1] if (img!=None and len(img_list)>0) else False)

        
#-------------------------------------------------------------------------------
# OPTIONS SUB-PANEL
#-------------------------------------------------------------------------------
# Expand Background Sub-panel
class EIL_PT_MaterialListPanel_Options(Panel):
    bl_space_type  = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_label = "Options"
    bl_parent_id = "EML_PT_Panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        cs = context.scene
        props = cs.extra_material_list

        layout.use_property_split = True
        layout.use_property_decorate = False

        #-----------------------------------------------------------------------
        # SETTINGS
        #-----------------------------------------------------------------------
        # print("bl %s" % bpy.app.version[1])
        if (bpy.app.version[1] < 90):
            column = layout.column(align=True)
            column.label(text="Show")
        else:
            column = layout.column(heading="Show", align=True)
        column.prop(props, "show_icons")
        column.prop(props, "info")
        #--- List style buttons
        #--- Num. of rows & cols for image preview list		
        if (bpy.app.version[1] < 90):
            column = layout.column(align=True)
            column.label(text="Preview Style")
        else:
            column = layout.column(heading="Preview Style", align=True)
        column.prop(props, "style") #,expand=True
        if props.style =='PREVIEW':
            column.prop(props, "rows")
            column.prop(props, "cols")

        layout.use_property_split = True
        if (bpy.app.version[1] < 90):
            op = layout.column(align=True)
            op.label(text="Clean")
        else:
            op = layout.column(heading="Clean", align=True)
        op.prop(props,"clean_enabled", text="Duplicates")

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=False)
        flow.active = props.clean_enabled
        flow.enabled = props.clean_enabled
        # flow.prop(props, "clear_mode", text="")
        # flow.operator("extra_image_list.clear", text="Clear", icon='ERROR')

        #-----------------------------------------------------------------------
        # ELIMINATE Duplicates
        #-----------------------------------------------------------------------
        # row = layout.row()
        # row.label(text="Eliminate Duplicates:", icon='DUPLICATE')
        # flow = layout.row(align=True)
        flow.operator("extra_material_list.eliminate_nodegroups", text="Node Groups")
        flow.operator("extra_material_list.eliminate_materials", text="Materials")



#-- EML WM DIALOG MENU __#
class EML_OT_ImageListWM(Operator):
    bl_idname = "eml.imagelist_wm"
    bl_name = "Extra Image List Menu"
    bl_label = "Extra Image List WM"

    #--- Available only for "shading nodes" render
    @classmethod
    def poll(cls, context):
        snode = context.space_data
        node_types = {'OBJECT','WORLD'}
        # if snode.shader_type in node_types:
        # mat = context.active_object.active_material.use_nodes
        return snode.tree_type == 'ShaderNodeTree' #mat and  snode.node_tree is not None

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Extra Material List")

    def draw(self, context):
        layout = self.layout
        cs = context.scene
        ob = context.object
        sdata = context.space_data
        props = cs.extra_material_list

        # WM operator doesnt seem to have header
        layout.label(text="Extra Material List")

        #--- Shader tree and type selection
        row = layout.row()
        row.alignment = 'CENTER'
        row.prop(props, "shaderType",expand=True)

        #--- Proceed only for OBJECT/WORLD shader node trees
        if sdata.tree_type != 'ShaderNodeTree' or (sdata.shader_type != 'OBJECT' and sdata.shader_type != 'WORLD'):
            return

        #--- List style buttons
        row = layout.row()
        # row.prop(props, "style", expand=True)

        #-----------------------------------------------------------------------
        # PREVIEW Style
        #-----------------------------------------------------------------------
        if props.style == 'PREVIEW':

            #--- Num. of rows & cols for the preview list            
            # col = split.column(align=True)
            # col.prop(props, "rows")
            # col.prop(props, "cols")

            #--- Object materials
            if sdata.shader_type == 'OBJECT':

                # List of all scene materials
                mat_list = bpy.data.materials

                # Current active material
                if hasattr(sdata.id_from, "active_material"):
                    mat = sdata.id_from.active_material
                else:
                    return

                layout.label(text=ob.name, icon='OUTLINER_OB_MESH')
                # From blender node_space
                if sdata.shader_type == 'OBJECT' and ob:
                    
                    types_that_support_material = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META',
                                            'GPENCIL', 'VOLUME', 'HAIR', 'POINTCLOUD'}
                    # disable material slot buttons when pinned, cannot find correct slot within id_from (T36589)
                    ob_type = ob.type
                    # disable also when the selected object does not support materials
                    has_material_slots = not sdata.pin and ob_type in types_that_support_material

                    if ob_type != 'LIGHT':
                        row = layout.row()
                        row.enabled = has_material_slots
                        row.ui_units_x = 4
                        if (bpy.app.version[1] < 90):
                            row = layout.column(align=True)
                            row.label(text="Material Slot")
                        else:
                            row = row.column(heading="Material Slot")
                        row.popover(panel="EML_PT_material_slots")
                        # row.popover(panel="EML_PT_material_slots", text="Material Slot")
                        
                # Preview list
                ob = context.active_object
                objs = {'MESH'}
                sub = layout.row()
                sub.enabled = ob.type in objs # Disable when not mesh objects
                sub.template_ID_preview(
                    ob, "active_material", # changed to OB so we dont get greasepencil materials
                    new = "material.new",
                    rows = props.rows, cols = props.cols)

                row = layout.row()
                split = row.split(factor=0.5)
                # Navigation button PREV
                sub = split.column()
                sub.scale_y = 1.5
                sub.operator("extra_material_list.nav", text="", icon='BACK').dir = 'PREV'
                sub.enabled = enable_prev_button(mat, mat_list)

                # Navigation button NEXT
                sub = split.column()
                sub.scale_y = 1.5
                sub.operator("extra_material_list.nav", text="", icon='FORWARD').dir = 'NEXT'
                sub.enabled = enable_next_button(mat, mat_list)
                
                # Show Texture list if possible
                try:
                    # mNode = context.active_object.active_material.node_tree.nodes.active
                    if bpy.context.active_object.active_material:
                        mNode = bpy.context.active_object.active_material.node_tree.nodes.active
                        if mNode!=None:
                            if mNode.type=='GROUP':
                                mNode = mNode.node_tree.nodes.active
                    if mNode.type == 'TEX_IMAGE':
                        layout.label(text=mNode.name, icon='TEXTURE')
                        layout.template_ID_preview(
                        mNode, "image",
                        new = "image.new",
                        open = "image.open",
                        rows = props.rows, cols = props.cols)
                except:
                    pass
                

            #--- World materials
            elif sdata.shader_type == 'WORLD':

                # List of all scene worlds
                world_list = bpy.data.worlds

                # Current active world
                world = context.scene.world

                # Preview list
                layout.template_ID_preview(
                cs, "world",
                new = "world.new",
                rows = props.rows, cols = props.cols)

                row = layout.row()
                split = row.split(factor=0.5)
                # Navigation button PREV
                sub = split.column()
                sub.scale_y = 1.5
                sub.operator("extra_material_list.nav", text="", icon='BACK').dir = 'PREV'
                sub.enabled = enable_prev_button(world, world_list)
                
                # Navigation button NEXT
                sub = split.column()
                sub.scale_y = 1.5
                sub.operator("extra_material_list.nav", text="", icon='FORWARD').dir = 'NEXT'
                sub.enabled = enable_next_button(world, world_list)
                
                # Show Texture list if possible
                try:
                    wNode = world.node_tree.nodes.active
                    if wNode.type == 'TEX_ENVIRONMENT':
                        layout.label(text=wNode.name, icon='TEXTURE')
                        layout.template_ID_preview(
                        wNode, "image",
                        new = "image.new",
                        open = "image.open",
                        rows = props.rows, cols = props.cols
                    )
                except:
                    pass
                
            # layout.separator()

        # -----------------------------------------------------------------------
        # LIST Style
        # -----------------------------------------------------------------------
        elif props.style == 'LIST':
            
            # From blender node_space
            if sdata.shader_type == 'OBJECT' and ob:
                
                types_that_support_material = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META',
                                        'GPENCIL', 'VOLUME', 'HAIR', 'POINTCLOUD'}
                # disable material slot buttons when pinned, cannot find correct slot within id_from (T36589)
                ob_type = ob.type
                # disable also when the selected object does not support materials
                has_material_slots = not sdata.pin and ob_type in types_that_support_material

                if ob_type != 'LIGHT':
                    row = layout.row()
                    row.enabled = has_material_slots
                    row.ui_units_x = 4
                    if (bpy.app.version[1] < 90):
                        row = layout.column(align=True)
                        row.label(text="Material Slot")
                    else:
                        row = row.column(heading="Material Slot")
                    row.popover(panel="EML_PT_material_slots")
                    # row.popover(panel="EML_PT_material_slots", text="Material Slot")
                        
                        
            #--- Object materials
            if sdata.shader_type == 'OBJECT':
                layout.template_list(
                    "EML_UL_MaterialList", "",
                    bpy.data, "materials", #bpy.data
                    props, "material_id",
                    # rows = len(bpy.data.materials)
                )

                # Show Texture list if possible
                try:
                    # mNode = context.active_object.active_material.node_tree.nodes.active
                    if bpy.context.active_object.active_material:
                        mNode = bpy.context.active_object.active_material.node_tree.nodes.active
                        if mNode!=None:
                            if mNode.type=='GROUP':
                                mNode = mNode.node_tree.nodes.active
                    if mNode.type == 'TEX_IMAGE':
                        layout.label(text=mNode.name, icon='TEXTURE')
                        layout.template_ID_preview(
                        mNode, "image",
                        new = "image.new",
                        open = "image.open",
                        rows = props.rows, cols = props.cols)
                except:
                    pass

            #--- World materials
            elif sdata.shader_type == 'WORLD':

                # Current active world
                world = context.scene.world

                layout.template_list(
                    "EML_UL_MaterialList", "",
                    bpy.data, "worlds",
                    props, "world_id",
                    rows = len(bpy.data.worlds)
                )

                # Show Texture list if possible
                try:
                    wNode = world.node_tree.nodes.active
                    if wNode.type == 'TEX_ENVIRONMENT':
                        layout.label(text=wNode.name, icon='TEXTURE')
                        layout.template_ID_preview(
                        wNode, "image",
                        new = "image.new",
                        open = "image.open",
                        rows = props.rows, cols = props.cols)
                except:
                    pass


    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)
        # return context.window_manager.invoke_props_dialog(self) # shows header but also OK btn > we dont need that

#--------------------------------------------------------

# Functions to decide if enable/disable navigation buttons
#-------------------------------------------------------------------------------
def enable_prev_button(item, item_list):
    if item != None and len(item_list) > 0:
        return item != item_list[0]
    else:
        return False

def enable_next_button(item, item_list):
    if item != None and len(item_list) > 0:
        return item != item_list[-1]
    else:
        return False


#-------------------------------------------------------------------------------
# CUSTOM TEMPLATE_LIST FOR MATERIALS
#-------------------------------------------------------------------------------
class EML_UL_MaterilList(UIList):
    bl_idname = "EML_UL_MaterialList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        props = bpy.context.scene.extra_material_list

        # Material name and icon
        row = layout.row(align=True)
        if props.show_icons:
            row.prop(item, "name", text="", emboss=False, icon_value=icon)
        else:
            row.prop(item, "name", text="", emboss=False, icon_value=0)

        # Material status (fake user, zero users)
        row = row.row(align=True)
        row.alignment = 'RIGHT'

        # if item.use_fake_user:
            # row.label(text="F")
        # Allows us to edit it from the list
        row.prop(item, "use_fake_user", text="", emboss=False)
        # else:
        if item.users == 0:
            row.label(text="0")

def update_shader_type(self,context):
    sdata = context.space_data
    cs = context.scene
    ob = context.object
    sdata = context.space_data
    props = cs.extra_material_list
    sdata.shader_type = props.shaderType

#--- Update the active material when you select another item in the template_list
def update_active_material(self, context):
    try:
        id = bpy.context.scene.extra_material_list.material_id
        if id < len(bpy.data.materials):
            mat = bpy.data.materials[id]
            bpy.context.object.active_material = mat
    except:
        pass

#--- Update the active world shader when you select another item in the template_list
def update_active_world(self, context):
    try:
        id = bpy.context.scene.extra_material_list.world_id
        if id < len(bpy.data.worlds):
            world = bpy.data.worlds[id]
            bpy.context.scene.world = world
    except:
        pass


#-------------------------------------------------------------------------------
# ELIMINATE MATERIAL DUPLICATES
#-------------------------------------------------------------------------------
class EML_PT_EliminateMaterials(Operator):
    bl_idname = "extra_material_list.eliminate_materials"
    bl_label = "Eliminate Material Duplicates"
    bl_description = "Eliminate material duplicates (ending with .001, .002, etc) and replace them with the original material if found."

    def execute(self, context):
        print("\nEliminate Material Duplicates:")
        mats = bpy.data.materials

        #--- Search for mat. slots in all objects
        for obj in bpy.data.objects:
            for slot in obj.material_slots:

                # Get the material name as 3-tuple (base, separator, extension)
                (base, sep, ext) = slot.name.rpartition('.')

                # Replace the numbered duplicate with the original if found
                if ext.isnumeric():
                    if base in mats:
                        print("  For object '%s' replace '%s' with '%s'" % (obj.name, slot.name, base))
                        slot.material = mats.get(base)

        return{'FINISHED'}


#-------------------------------------------------------------------------------
# ELIMINATE NODE GROUP DUPLICATES
#-------------------------------------------------------------------------------
class EML_PT_EliminateNodeGroups(Operator):
    bl_idname = "extra_material_list.eliminate_nodegroups"
    bl_label = "Eliminate Node Group Duplicates"
    bl_description = "Eliminate node group duplicates (ending with .001, .002, etc) and replace them with the original node group if found."

    #--- Eliminate node group duplicate with the original group found
    def eliminate(self, node):
        node_groups = bpy.data.node_groups

        # Get the node group name as 3-tuple (base, separator, extension)
        (base, sep, ext) = node.node_tree.name.rpartition('.')

        # Replace the numbered duplicate with original if found
        if ext.isnumeric():
            if base in node_groups:
                print("  Replace '%s' with '%s'" % (node.node_tree.name, base))
                node.node_tree.use_fake_user = False
                node.node_tree = node_groups.get(base)

    #--- Execute
    def execute(self, context):
        print("\nEliminate Node Group Duplicates:")

        mats = list(bpy.data.materials)
        worlds = list(bpy.data.worlds)
        node_groups = bpy.data.node_groups

        #--- Search for duplicates in the actual node groups
        for group in node_groups:
            for node in group.nodes:
                if node.type == 'GROUP':
                    self.eliminate(node)

        #--- Search for duplicates in materials
        for mat in mats + worlds:
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'GROUP':
                        self.eliminate(node)

        return{'FINISHED'}


#-------------------------------------------------------------------------------
# NAVIGATION OPERATOR
#-------------------------------------------------------------------------------
class EML_OT_Nav(Operator):
    bl_idname = "extra_material_list.nav"
    bl_label = "Nav"
    bl_description = "Navigation button"

    dir : EnumProperty(
        items = [
            ('NEXT', "PREV", "PREV"),
            ('PREV', "PREV", "PREV")
        ],
        name = "dir",
        default = 'NEXT')

    def execute(self, context):
        sdata = context.space_data

        #--- Navigate in object materials
        if sdata.shader_type == 'OBJECT':

            # List of all scene materials
            mat_list = list(bpy.data.materials)

            # Get index of the current active material
            mat = sdata.id_from.active_material
            if mat in mat_list:
                id = mat_list.index(mat)
            else:
                return{'FINISHED'}

            # Navigate
            if self.dir == 'NEXT':
                if id+1 < len(mat_list):
                    sdata.id_from.active_material = mat_list[id+1]

            if self.dir == 'PREV':
                if id > 0:
                    sdata.id_from.active_material = mat_list[id-1]

        #--- Navigate in worlds
        elif sdata.shader_type == 'WORLD':

            # List of all scene worlds
            world_list = list(bpy.data.worlds)

            # Get index of the current active world
            world = context.scene.world
            if world in world_list:
                id = world_list.index(world)
            else:
                return{'FINISHED'}

            # Navigate
            if self.dir == 'NEXT':
                if id+1 < len(world_list):
                    context.scene.world = world_list[id+1]

            if self.dir == 'PREV':
                if id > 0:
                    context.scene.world = world_list[id-1]

        return{'FINISHED'}


#-------------------------------------------------------------------------------
# CUSTOM HANDLER (scene_update_post)
# - This handler is invoked after the scene updates
# - Keeps template_list synced with the active material
#-------------------------------------------------------------------------------
@persistent
def update_material_list(context):
    try:
        props = bpy.context.scene.extra_material_list

        #--- Update world list
        try:
            world = bpy.context.scene.world
            if world != None:
                id = bpy.data.worlds.find(world.name)
                if id != -1 and id != props.world_id:
                    props.world_id = id
        except:
            pass

        #--- Update material list
        try:
            mat = bpy.context.object.active_material
            if mat != None:
                id = bpy.data.materials.find(mat.name)
                if id != -1 and id != props.material_id:
                    props.material_id = id
        except:
            pass
    except:
        pass


#-------------------------------------------------------------------------------
# CUSTOM SCENE PROPS
#-------------------------------------------------------------------------------
class ExtraMaterialList_Props(bpy.types.PropertyGroup):
    
    shaderType : EnumProperty(
        items = [
            ('OBJECT', "OBJECT", "Object",'OBJECT_DATA', 0),
            ('WORLD', "WORLD", "Object",'WORLD', 1),
        ],
        # default = '',
        name = "Shader Type",
        description = "Select Shader Type",
        update = update_shader_type)

    style : EnumProperty(
        items = [
            ('PREVIEW', "Preview", "", 0),
            ('LIST', "List", "", 1),
        ],
        default = 'PREVIEW',
        name = "Style",
        description = "Material list style")

    rows : IntProperty(
        name = "Rows",
        description = "Num. of rows in the preview list",
        default = 4, min = 1, max = 15)

    cols : IntProperty(
        name = "Cols",
        description = "Num. of columns in the preview list",
        default = 6, min = 1, max = 30)

    # Index of the active material in the template_list
    material_id : IntProperty(
        default = 0,
        update = update_active_material)

    # Index of the active world in the template_list
    world_id : IntProperty(
        default = 0,
        update = update_active_world)

    show_icons : BoolProperty(
        name = "Material icons",
        default = False)

    info : BoolProperty(
        name="Texture info",
        default=False)

    clean_enabled : BoolProperty(
            default=False,
            name="Clean:",
            description="Enables option to clear scene of image textures. Be careful!")

#-- ADDON PREFS --#
class EML_AddonPreferences(AddonPreferences):
    """ Preference Settings Addin Panel"""
    bl_idname = __name__
    bl_label = "Addon Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        #col.separator()
        col.label(text = "Hotkeys:")
        col.label(text = "Do NOT remove hotkeys, disable them instead!")

        col.separator()
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        col.separator()
        km = kc.keymaps['Node Editor']
        kmi = registers.get_hotkey_entry_item(km, 'eml.imagelist_wm', 'EXECUTE','tab')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            col.label(text = "Opens the popup window")
        else:
            col.label(text = "Alt + Shift + 1 = opens the popup window")
            col.label(text = "restore hotkeys from interface tab")
        col.separator()



#-------------------------------------------------------------------------------
# REGISTER/UNREGISTER ADDON CLASSES
#-------------------------------------------------------------------------------
addon_keymaps = []

classes = [
    EML_PT_material_slots,
    EML_PT_Panel,
    EIL_PT_MaterialListPanel_Options,
    EML_AddonPreferences,
    EML_OT_ImageListWM,
    EML_UL_MaterilList,
    EML_PT_EliminateMaterials,
    # 2.8 PROPS NEED TO BE ADDED???
    ExtraMaterialList_Props,
    EML_PT_EliminateNodeGroups,
    EML_OT_Nav
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.extra_material_list = PointerProperty(type=ExtraMaterialList_Props)
    bpy.app.handlers.depsgraph_update_post.append(update_material_list)

    # Keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps.new(name = "Node Editor", space_type = "NODE_EDITOR")

    kmi = km.keymap_items.new("eml.imagelist_wm", "NUMPAD_1", "PRESS", alt = True, shift = True)
    # kmi.properties.tab = "EXECUTE"
    addon_keymaps.append((km, kmi))

    # updater.check(bl_info)
    # updater.register()


def unregister():
    # updater.unregister()

    del bpy.types.Scene.extra_material_list
    bpy.app.handlers.depsgraph_update_post.remove(update_material_list)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

        
if __name__ == "__main__":
    register()