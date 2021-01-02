###########################################################################
#
# This module contains functions to transform dictionaries of actions into
# the API-formatted string commands
#
###########################################################################

def cameo_dict_to_string_router(input_dict):
    if input_dict['action'] == 'create':
        return cameo_creation_dict_to_string(input_dict)
    elif input_dict['action'] == 'setMeta':
        return cameo_metaprop_single_set_dict_to_string(input_dict)
    elif input_dict['action'] == 'setMetaList':
        return cameo_metaprop_list_set_dict_to_string(input_dict)
    elif input_dict['action'] == 'applyStereo':
        return cameo_stereotype_dict_to_string(input_dict)
    elif input_dict['action'] == 'getAtts':
        return cameo_gather_dict_to_string(input_dict)
    elif input_dict['action'] == 'getAttsByName':
        return cameo_gather_dict_by_name_to_string(input_dict)

def cameo_creation_dict_to_string(input_dict):
    return input_dict['temp_var'] + " = " + input_dict['create_expr'] + ';'

def cameo_metaprop_single_set_dict_to_string(input_dict):
    return input_dict['target_temp_name'] + '.' + input_dict['command'] + '(' + \
        input_dict['value_to_set'] + ');'

def cameo_metaprop_list_set_dict_to_string(input_dict):
    return 'temp_list = ' + input_dict['target_temp_name'] + '.' + input_dict['get_command'] + '();' + \
        '\ntemp_list.addAll(' + input_dict['value_to_set'] + ');'

def cameo_stereotype_dict_to_string(input_dict):
    return 'com.nomagic.uml2.ext.jmi.helpers.StereotypesHelper.addStereotypeByString(' + \
        input_dict['target_temp_name'] + ', \"' + input_dict['stereo'] + '\"' + ');'

def cameo_gather_dict_to_string(input_dict):
    if input_dict['is_list']:
        if input_dict['specific_item'] == '*':
            return input_dict['value_to_return'] + ' = null;\n' + \
                'for (itm in ' + input_dict['target_temp_name'] + '.' + \
                input_dict['command'] + ') {\n' + '   ' + input_dict['value_to_return'] + \
                ' = itm;\n}'
        else:
            return 'counter = 0;\n' + input_dict['value_to_return'] + ' = null;\n' + \
                   'for (itm in ' + input_dict['target_temp_name'] + '.' + \
                   input_dict['command'] + ') {\n' + \
                   '  if (counter == ' + str(input_dict['specific_item']) + ') {\n' + \
                   '   ' + input_dict['value_to_return'] + \
                   ' = itm;\n    counter = counter + 1;\n}}'
    else:
        return input_dict['value_to_return'] + ' = ' + \
            input_dict['target_temp_name'] + '.' + input_dict['command']

def cameo_gather_dict_by_name_to_string(input_dict):
    if input_dict['is_list']:
        return input_dict['value_to_return'] + ' = null;\n' + \
            'for (itm in ' + input_dict['target_temp_name'] + '.' + \
            input_dict['command'] + ') {\n' + \
            '  if (itm.getName().equals(\"' + input_dict['specific_item'] + '\")) {\n'\
            '   ' + input_dict['value_to_return'] + \
            ' = itm;\n}}'

    else:
        return input_dict['value_to_return'] + ' = ' + \
            input_dict['target_temp_name'] + '.' + input_dict['command']


def cameo_find_model_root_strings():
    strings = []
    strings.append('modelBase = com.nomagic.magicdraw.core.Application.' +
                   'getInstance().getProject().getPrimaryModel();')

    return strings

def cameo_build_session_start():
    strings = []
    strings.append('myElementsFactory = com.nomagic.magicdraw.core.Application.getInstance().' +
                   'getProject().getElementsFactory();')
    strings.append('pem = com.nomagic.magicdraw.openapi.uml.' +
                   'PresentationElementsManager.getInstance();')
    strings.append('mem = com.nomagic.magicdraw.openapi.uml.' +
                   'ModelElementsManager.getInstance();')
    strings.extend(cameo_find_model_root_strings())
    strings.append('com.nomagic.magicdraw.openapi.uml.' +
                   'SessionManager.getInstance().createSession(\"Cameo build.\");\n')
    return strings

def cameo_build_session_end():
    strings = []
    strings.append('com.nomagic.magicdraw.openapi.uml.' +
                   'SessionManager.getInstance().closeSession();')
    return strings

######################## LIBRARY SECTION ####################################

library_element_ids = {'Real ValueType': '\"_11_5EAPbeta_be00301_1147431819399_50461_1671\"'}
library_element_vars = {'Real ValueType': 'realVal'}

def access_libraries():
    strings = []
    strings.append(
        library_element_vars['Real ValueType'] + ' = \n'
                                                 '    com.nomagic.magicdraw.core.Application.getInstance().getProject().getElementByID(' +
        library_element_ids['Real ValueType'] + ');\n'
    )

    return strings