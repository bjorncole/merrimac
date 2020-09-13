###########################################################################
#
# Cameo API commands and data settings
#
###########################################################################

########################## CREATE COMMANDS ################################

def cameo_element_creation_dict(temp_var_name='', factory_handle_name='', meta_element=''):
    return {
        'action': 'create',
        'temp_var': temp_var_name,
        'create_expr': factory_handle_name + '.create' + meta_element + 'Instance()',
        'metatype': meta_element
    }

def cameo_pres_shape_creation_dict(temp_var_name='',
                                     factory_handle_name='',
                                     meta_element='',
                                     presented_element=''):
    return {
        'action': 'create PE',
        'temp_var': temp_var_name,
        'metatype': meta_element,
        'factory_handle': factory_handle_name,
        'presented element': presented_element
    }

########################## MODIFY COMMANDS ################################

def cameo_metaprop_single_set_dict(temp_var_name='', meta_prop='', value=''):
    return {
        'action': 'setMeta',
        'target_temp_name': temp_var_name,
        'command': 'set' + meta_prop,
        'value_to_set': value
    }

def cameo_apply_stereotype_dict(temp_var_name='', stereo_name=''):
    return {
        'action': 'applyStereo',
        'target_temp_name': temp_var_name,
        'stereo': stereo_name
    }