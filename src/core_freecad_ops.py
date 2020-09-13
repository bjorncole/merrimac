###########################################################################
#
# PartDesign workbench commands and settings
# Workbench workflow is body -> sketch -> 3d operation (e.g., pad or revolve)
#
###########################################################################

########################## CREATE COMMANDS ################################

def freecad_create_dict(mod='PartDesign',
                        kind='Body',
                        name='Body',
                        parent='',
                        paras=[]):
    """
    Generates a standard format describing a command to create a FreeCAD object

    :param mod: The FreeCAD module in which the object to be created is cataloged
    :param kind: The kind of FreeCAD object
    :param name: The name to be assigned on creation
    :param parent: The object that will own the new object
    :param paras: Parameters that the object may take upon creation
    :return: A dictionary that represents the command and its parameters
    """


    return {
        'action': 'create',
        'module': mod,
        'object': kind,
        'name': name,
        'parent name': parent,
        'parameters': paras
    }

####################### MODIFY COMMANDS ###################################

def freecad_set_document_field_dict(obj='', att='', value=''):
    """
    Generates a command to modify a field of a FreeCAD object

    :param obj: The object to modify
    :param att: The attribute to be modified
    :param value: The value to assign to the attribute
    :return:
    """

    return {
        'action': 'set',
        'object': obj,
        'attribute': att,
        'value': value
    }

def freecad_set_gui_field_dict(obj='', att='', value=''):
    """
    Generates a command to modify a field of a GUI object

    :param obj: The object to modify
    :param att: The attribute to be modified
    :param value: The value to assign to the attribute
    :return:
    """

    return {
        'action': 'set GUI',
        'object': obj,
        'attribute': att,
        'value': value
    }

################ MODIFY APPLICATION WORKING STATE ########################

def freecad_set_document_edit_dict(obj=''):
    """
    Assign the object to be edited in the GUI

    :param obj:
    :return:
    """

    return {
        'action': 'set GUI edit',
        'object': obj
    }

def freecad_workbench_swap(workbench_activate=''):
    return {
        'action': 'swap_workbench',
        'workbench': workbench_activate,
    }

def freecad_exec_gui_command(command=''):
    return {
        'action': 'exec GUI command',
        'command': command
    }

def freecad_add_selection(sel_path=['\'Unnamed\'']):
    return {
        'action': 'add selection',
        'selection path': sel_path
    }

def freecad_clear_select():
    return {
        'action': 'clear selection'
    }

def freecad_set_activedocument(doc_name='Unnamed'):
    return {
        'action': 'set active document',
        'document': doc_name
    }

################ FILE OPERATIONS ########################

def freecad_save_file(file_name='', directory=''):
    return {
        'action': 'save',
        'file name': file_name,
        'directory': directory
    }