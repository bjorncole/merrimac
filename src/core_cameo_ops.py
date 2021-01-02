###########################################################################
#
# Cameo API commands and data settings
#
###########################################################################

########################## CREATE COMMANDS ################################

def cameo_element_creation_dict(temp_var_name='', factory_handle_name='', meta_element=''):
    return {
        'action': 'create',
        'temp_var': temp_var_name, # meant to help find this object later for reuse
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

def cameo_metaprop_list_set_dict(temp_var_name='', meta_prop='', value=''):
    return {
        'action': 'setMetaList',
        'target_temp_name': temp_var_name,
        'get_command': 'get' + meta_prop,
        'value_to_set': value
    }

def cameo_apply_stereotype_dict(temp_var_name='', stereo_name=''):
    return {
        'action': 'applyStereo',
        'target_temp_name': temp_var_name,
        'stereo': stereo_name
    }

def cameo_gather_items(temp_var_name='', meta_prop='', return_value='', is_list=False, index='*'):
    return {
        'action': 'getAtts',
        'target_temp_name': temp_var_name,
        'command': 'get' + meta_prop + '()' if is_list else 'get' + meta_prop + '();',
        'value_to_return': return_value,
        'is_list': is_list,
        'specific_item': index
    }

def cameo_gather_item_by_name(temp_var_name='', meta_prop='', return_value='', is_list=False, name=''):
    return {
        'action': 'getAttsByName',
        'target_temp_name': temp_var_name,
        'command': 'get' + meta_prop + '()' if is_list else 'get' + meta_prop + '();',
        'value_to_return': return_value,
        'is_list': is_list,
        'specific_item': name
    }