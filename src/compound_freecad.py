from core_freecad_ops import *

###########################################################################
#
# This module contains classes and functions to build up lists of
# commands to execute simple actions in FreeCAD such as starting
# a sketch or drawing a rectangle upon that sketch.
#
###########################################################################

######################## BASIC CLASSES ###############################

class T_CAD_Body():
    def __init__(self):
        self.b_name = ''

    def generate_for_freecad(self):
        instructions_list = []

        # dicts for general part building

        wb_dict = freecad_workbench_swap(workbench_activate='PartDesignWorkbench')
        body_dict = freecad_create_dict(
            name=self.b_name,
            mod='PartDesign',
            kind='Body'
        )

        # rename the elements of the local coordinate system to make it more specific

        instructions_list.append(wb_dict)
        instructions_list.append(body_dict)

        return instructions_list


class T_Geom_Rect_Prism(T_CAD_Body):
    def __init__(self):
        super().__init__()
        self.p_width = 0.0
        self.p_height = 0.0
        self.p_length = 0.0
        self.p_plane = 'XZ_Plane'

    def generate_for_freecad(self):
        instructions_list = super().generate_for_freecad()

        # create sketch

        sketch_dicts = freecad_start_sketch_dicts(
            body_name=self.b_name,
            name=self.b_name + '_Face',
            plane=self.p_plane
        )

        instructions_list.extend(sketch_dicts)

        # draw the basis rectangle on the sketch

        rect_dicts = freecad_centered_rectangle_create_dicts(width=self.p_width,
                                                                    height=self.p_height,
                                                                    sketch=self.b_name + '_Face')

        instructions_list.extend(rect_dicts)

        # extrude into full length

        pad_dicts = freecad_create_extrusion(
            extrude_length=self.p_length,
            body_name=self.b_name,
            sketch_name=self.b_name + '_Face'
        )

        instructions_list.extend(pad_dicts)

        return instructions_list

class T_Geom_Assembly():

    def __init__(self):
        self.part_types_dict = {}
        self.files_dict = {}

    def generate_for_freecad(self):
        instructions_list = []

        # single-file approach

        for part_name, part_type in self.part_types_dict.items():
            mult = self.part_mults_dict['part_name']

            new_list = part_type.generate_for_freecad()

            for step in new_list:
                instructions_list.append(step)

        return instructions_list

#################### SIMPLE SETS OF OPERATIONS #######################

def freecad_start_sketch_dicts(name='', plane='', body_name=''):
    sketch_start_dicts = []

    sketch_start_dicts.append(
        freecad_create_dict(
            name=name,
            parent=body_name,
            kind='SketchObject',
            mod='Sketcher'
        )
    )

    sketch_start_dicts.append(freecad_set_document_field_dict(
        obj=name,
        att='Support',
        value='(App.activeDocument().' + plane + ', [\'\'])')
    )

    sketch_start_dicts.append(freecad_set_document_field_dict(
        obj=name,
        att='MapMode',
        value='\'FlatFace\'')
    )

    sketch_start_dicts.append(freecad_set_document_edit_dict(obj='\'' + name + '\''))

    return sketch_start_dicts

def freecad_centered_rectangle_create_dicts(width=0.1, height=0.1, sketch='Sketch'):
    rect_dicts = []

    # make the lines

    rect_dicts.append(
        freecad_create_dict(
            paras = {
                'StartPoint': [-width / 2.0, height / 2.0, 0.0],
                'EndPoint': [width / 2.0, height / 2.0, 0.0]
            },
            parent=sketch,
            mod='Part',
            kind='LineSegment'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'StartPoint': [width / 2.0, height / 2.0, 0.0],
                'EndPoint': [width / 2.0, -height / 2.0, 0.0]
            },
            parent=sketch,
            mod='Part',
            kind='LineSegment'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'StartPoint': [width / 2.0, -height / 2.0, 0.0],
                'EndPoint': [-width / 2.0, -height / 2.0, 0.0]
            },
            parent=sketch,
            mod='Part',
            kind='LineSegment'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'StartPoint': [-width / 2.0, -height / 2.0, 0.0],
                'EndPoint': [-width / 2.0, height / 2.0, 0.0]
            },
            parent=sketch,
            mod='Part',
            kind='LineSegment'
        )
    )

    # constrain the lines to touch


    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'Coincident',
                'fromLine': 0,
                'fromPoint': 2,
                'toLine': 1,
                'toPoint': 1
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'Coincident',
                'fromLine': 1,
                'fromPoint': 2,
                'toLine': 2,
                'toPoint': 1
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'Coincident',
                'fromLine': 2,
                'fromPoint': 2,
                'toLine': 3,
                'toPoint': 1
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'Coincident',
                'fromLine': 3,
                'fromPoint': 2,
                'toLine': 0,
                'toPoint': 1
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    # make the lines straight

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'Horizontal',
                'line': 0
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'Horizontal',
                'line': 2
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'Vertical',
                'line': 1
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'Vertical',
                'line': 3
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    # position the corners

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'DistanceX',
                'fromLine': -1,
                'fromPoint': 1,
                'toLine': 0,
                'toPoint': 2,
                'distance': width / 2.0
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'DistanceX',
                'fromLine': 0,
                'fromPoint': 1,
                'toLine': -1,
                'toPoint': 1,
                'distance': width / 2.0
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'DistanceY',
                'fromLine': -1,
                'fromPoint': 1,
                'toLine': 0,
                'toPoint': 2,
                'distance': height / 2.0
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    rect_dicts.append(
        freecad_create_dict(
            paras={
                'type': 'DistanceY',
                'fromLine': 1,
                'fromPoint': 2,
                'toLine': -1,
                'toPoint': 1,
                'distance': height / 2.0
            },
            parent=sketch,
            mod='Sketcher',
            kind='Constraint'
        )
    )

    return rect_dicts


def freecad_create_extrusion(extrude_length=1000.0, body_name='Body', sketch_name='Sketch'):
    instructions_list = []

    pad_dict = freecad_create_dict(
        name=body_name + '_Pad',
        parent=body_name,
        mod='PartDesign',
        kind='Pad'
    )

    profile_dict = freecad_set_document_field_dict(
        obj=body_name + '_Pad',
        att='Profile',
        value='App.activeDocument().' + sketch_name
    )

    pad_to_plane_dict = freecad_set_document_field_dict(
        obj=body_name + '_Pad',
        att='Length',
        value=extrude_length
    )

    pad_out_dict = freecad_set_document_field_dict(
        obj=body_name + '_Pad',
        att='Length2',
        value=extrude_length
    )

    pad_att_dict1 = freecad_set_document_field_dict(
        obj=body_name + '_Pad',
        att='Type',
        value=0
    )

    pad_att_dict2 = freecad_set_document_field_dict(
        obj=body_name + '_Pad',
        att='UpToFace',
        value=None
    )

    pad_att_dict3 = freecad_set_document_field_dict(
        obj=body_name + '_Pad',
        att='Reversed',
        value=0
    )

    pad_att_dict4 = freecad_set_document_field_dict(
        obj=body_name + '_Pad',
        att='Midplane',
        value=0
    )

    pad_att_dict5 = freecad_set_document_field_dict(
        obj=body_name + '_Pad',
        att='Offset',
        value=0.0000
    )

    pad_gui_dict1 = freecad_set_gui_field_dict(
        obj=body_name + '_Pad',
        att='ShapeColor',
        value='Gui.ActiveDocument.' + body_name + '.ShapeColor'
    )

    pad_gui_dict2 = freecad_set_gui_field_dict(
        obj=body_name + '_Pad',
        att='LineColor',
        value='Gui.ActiveDocument.' + body_name + '.LineColor'
    )

    pad_gui_dict3 = freecad_set_gui_field_dict(
        obj=body_name + '_Pad',
        att='PointColor',
        value='Gui.ActiveDocument.' + body_name + '.PointColor'
    )

    pad_gui_dict4 = freecad_set_gui_field_dict(
        obj=body_name + '_Pad',
        att='Transparency',
        value='Gui.ActiveDocument.' + body_name + '.Transparency'
    )

    pad_gui_dict5 = freecad_set_gui_field_dict(
        obj=body_name + '_Pad',
        att='DisplayMode',
        value='Gui.ActiveDocument.' + body_name + '.DisplayMode'
    )

    instructions_list.append(pad_dict)
    instructions_list.append(profile_dict)
    instructions_list.append(pad_to_plane_dict)
    instructions_list.append(pad_out_dict)
    instructions_list.append(pad_att_dict1)
    instructions_list.append(pad_att_dict2)
    instructions_list.append(pad_att_dict3)
    instructions_list.append(pad_att_dict4)
    instructions_list.append(pad_att_dict5)

    instructions_list.append(pad_gui_dict1)
    instructions_list.append(pad_gui_dict2)
    instructions_list.append(pad_gui_dict3)
    instructions_list.append(pad_gui_dict4)
    instructions_list.append(pad_gui_dict5)

    return instructions_list