###########################################################################
#
# This module contains functions to transform dictionaries of actions into
# the API-formatted string commands
#
###########################################################################

def freecad_dict_to_string_router(dikt):
    """
    Routes command dictionaries based on their content to string generators

    :param dikt: The dictionary representing a given core command
    :return: The specific command in concrete syntax
    """

    if dikt['action'] == 'create' and dikt['module'] == 'Part' and \
        dikt['object'] == 'LineSegment':
        return freecad_create_line_dict_to_string(dikt)
    elif dikt['action'] == 'create' and dikt['module'] == 'Sketcher' and \
        dikt['object'] == 'Constraint':
        if dikt['parameters']['type'] == 'Coincident':
            return freecad_create_coincident_constraint_to_string(dikt)
        elif dikt['parameters']['type'] == 'Horizontal':
            return freecad_create_horizontal_constraint_to_string(dikt)
        elif dikt['parameters']['type'] == 'Vertical':
            return freecad_create_vertical_constraint_to_string(dikt)
        elif dikt['parameters']['type'] == 'DistanceX' or dikt['parameters']['type'] == 'DistanceY':
            return freecad_create_distance_constraint_to_string(dikt)
    elif dikt['action'] == 'create' and dikt['module'] == 'PartDesign' \
      and dikt['object'] == 'Body':
        return freecad_body_create_dict_to_string(dikt)
    elif dikt['action'] == 'create' and dikt['module'] == 'PartDesign' \
      and dikt['object'] == 'Pad':
        return freecad_create_pad_strings(dikt)
    elif dikt['action'] == 'create' and dikt['object'] == 'SketchObject':
        return freecad_sketch_create_string(dikt)
    elif dikt['action'] == 'set':
        return freecad_set_document_field_string(dikt)
    elif dikt['action'] == 'set GUI':
        return freecad_set_gui_field_string(dikt)
    elif dikt['action'] == 'set GUI edit':
        return freecad_set_document_edit_string(dikt)
    elif dikt['action'] == 'exec GUI command':
        return freecad_exec_gui_command_string(dikt)
    elif dikt['action'] == 'swap_workbench':
        return freecad_workbench_swap_to_string(dikt)
    elif dikt['action'] == 'remove':
        return freecad_remove_object_string(dikt)
    elif dikt['action'] == 'add':
        return freecad_add_object_string(dikt)
    elif dikt['action'] == 'move link':
        return freecad_adjust_links_string(dikt)
    elif dikt['action'] == 'save':
        return freecad_save_file_string(dikt)

def freecad_create_line_dict_to_string(dikt):
    return 'App.ActiveDocument.' + dikt['parent name'] + '.addGeometry(' + \
        dikt['module'] + '.' + dikt['object'] + '(' + \
        'App.Vector' + str(dikt['parameters']['StartPoint']).replace('[', '(').replace(']', ')') + \
        ', App.Vector' + str(dikt['parameters']['EndPoint']).replace('[', '(').replace(']', ')') + \
        '), False)'

def freecad_create_coincident_constraint_to_string(dikt):
    return 'App.ActiveDocument.' + dikt['parent name'] + '.addConstraint([' + \
        dikt['module'] + '.' + dikt['object'] + '(\'' + \
        dikt['parameters']['type'] + '\',' + str(dikt['parameters']['fromLine']) + ',' + \
        str(dikt['parameters']['fromPoint']) + ',' + str(dikt['parameters']['toLine']) + ',' + \
        str(dikt['parameters']['toPoint']) + ')])'

def freecad_create_horizontal_constraint_to_string(dikt):
    return 'App.ActiveDocument.' + dikt['parent name'] + '.addConstraint([' + \
        dikt['module'] + '.' + dikt['object'] + '(\'' + \
        dikt['parameters']['type'] + '\',' + str(dikt['parameters']['line'])+ ')])'

def freecad_create_vertical_constraint_to_string(dikt):
    return 'App.ActiveDocument.' + dikt['parent name'] + '.addConstraint([' + \
        dikt['module'] + '.' + dikt['object'] + '(\'' + \
        dikt['parameters']['type'] + '\',' + str(dikt['parameters']['line'])+ ')])'

def freecad_create_distance_constraint_to_string(dikt):
    return 'App.ActiveDocument.' + dikt['parent name'] + '.addConstraint(' + \
        dikt['module'] + '.' + dikt['object'] + '(\'' + \
        dikt['parameters']['type'] + '\',' + str(dikt['parameters']['fromLine']) + ',' + \
        str(dikt['parameters']['fromPoint']) + ',' + str(dikt['parameters']['toLine']) + ',' + \
        str(dikt['parameters']['toPoint']) + ',' + str(dikt['parameters']['distance']) + '))'

def freecad_body_create_dict_to_string(dikt):
    return 'App.activeDocument().addObject(\'' + dikt['module'] + '::' + dikt['object'] + \
        '\',\'' + dikt['name'] + '\')'

def freecad_sketch_create_string(dikt):
    return 'App.activeDocument().' + dikt['parent name'] + '.newObject(' + '\'' + dikt['module'] + \
        '::' + dikt['object'] + '\',\'' + dikt['name'] + '\')'

def freecad_create_pad_strings(dikt):
    return 'App.activeDocument().' + dikt['parent name'] + '.newObject(' + '\'' + dikt['module'] + \
        '::' + dikt['object'] + '\', \'' + dikt['name'] + '\')'

def freecad_set_document_field_string(dikt):
    return 'App.activeDocument().' + dikt['object'] + '.' + dikt['attribute'] + ' = ' + \
        str(dikt['value'])

def freecad_set_gui_field_string(dikt):
    return 'Gui.activeDocument().' + dikt['object'] + '.' + dikt['attribute'] + ' = ' + \
        str(dikt['value'])

def freecad_set_document_edit_string(dikt):
    return 'Gui.activeDocument().setEdit(' + dikt['object'] + ')'

def freecad_workbench_swap_to_string(dikt):
    return 'Gui.activateWorkbench(\'' + dikt['workbench'] + '\')'

def freecad_exec_gui_command_string(dikt):
    return 'Gui.runCommand(\'' + dikt['command'] + '\', 0)'

def freecad_add_selection_string(dikt):
    path = ''
    return 'Gui.Selection.addSelection(' + ','.join(dikt['sel_path']) + ')'

def freecad_clear_select_string(dikt):
    return 'Gui.Selection.clearSelection()'

def freecad_set_activedocument_string(dikt):
    return 'App.setActiveDocument(\'' + dikt['document'] + '\')'

def freecad_remove_object_string(dikt):
    return 'App.getDocument(\'Unnamed\').getObject(\'' + dikt['old owner'] + '\')' + \
        '.removeObject(' + dikt['item'] + ')'

def freecad_add_object_string(dikt):
    return 'App.getDocument(\'Unnamed\').getObject(\'' + dikt['new owner'] + '\')' + \
        '.addObject(' + dikt['item'] + ')'

def freecad_adjust_links_string(dikt):
    return 'App.getDocument(\'Unnamed\').getObject(\'' + dikt['object'] + '\')' + \
        '.adjustRelativeLinks(' + dikt['target'] + ')'

def freecad_save_file_string(dikt):
    return 'App.getDocument(\'Unnamed\').saveAs(u\"' + dikt['directory'] + \
        dikt['file name'] + '.FCStd\")'

def freecad_build_session_start():
    return [
        'import FreeCAD',
        'import FreeCADGui',
        'FreeCAD.newDocument()',
        'FreeCADGui.activeDocument().activeView().viewDefaultOrientation()',
        'App.setActiveDocument("Unnamed")',
        'App.ActiveDocument=App.getDocument("Unnamed")',
        'Gui.ActiveDocument=Gui.getDocument("Unnamed")'
    ]

def freecad_build_session_end():
    return [
        'App.ActiveDocument.recompute()',
        'Gui.activeDocument().resetEdit()',
        'App.closeDocument(\"Unnamed\")'
    ]

