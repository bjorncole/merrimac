from core_cameo_ops import *
from core_cameo_commands import *

###########################################################################
#
# This module contains functions to build up lists of commands to execute
# simple actions in Cameo such as creating a block or value property with
# default value.
#
###########################################################################

####################### BASIC CLASSES ####################################

class T_Sysml_Block():
    def __init__(self, order):
        self.attributes_dict = {}
        self.att_types_dict = {}
        self.part_lower_mult_dict = {}
        self.part_upper_mult_dict = {}
        self.part_types_dict = {}
        self.ref_lower_mult_dict = {}
        self.ref_upper_mult_dict = {}
        self.ref_types_dict = {}
        self.order = order

    def generate_for_cameo_abstract(self, owner_name):
        instructions_list = []
        self_temp_var = ''
        try:
            self_temp_var = 'class_id_' + str(self.order)
            instructions_list.extend(cameo_block_create_dicts(
                name=self.attributes_dict['name'],
                temp_var_base='class_id_',
                order_start=self.order,
                owner_obj=owner_name
                )
            )
        except KeyError:
            print('No name for this object!')

        try:
            counter = self.order + 1
            for non_name, val in self.attributes_dict.items():
                if non_name != 'name':
                    new_dicts = \
                        cameo_value_prop_create_dicts(
                            name=non_name,
                            order_start=counter,
                            owner_obj='class_id_' + str(self.order),
                            val_type=library_element_vars[ \
                                self.att_types_dict[non_name] + ' ValueType']
                        )

                    counter = counter + 1

                    instructions_list.extend(new_dicts)

                    val_dicts = \
                        cameo_literalval_create_dicts(
                            order_start=str(counter),
                            owner_obj='prop_id_' + str(counter - 1),
                            lit_type=self.att_types_dict[non_name],
                            lit_val=str(self.attributes_dict[non_name])
                        )

                    instructions_list.extend(val_dicts)

                    counter = counter + 1
        except Exception:
            print('Error in property creation')
            raise

        try:
            for part, typ in self.part_types_dict.items():
                # TODO: Check for existence of Block already
                typ.order = counter
                sub_block_rows = typ.generate_for_cameo_abstract(owner_name)
                create_count = 0
                pp_name = ''
                typ_ref = ''

                for row in sub_block_rows:
                    if row['action'] == 'create':
                        create_count = create_count + 1
                        if row['metatype'] == 'Class':
                            name_look = True
                            typ_ref = row['temp_var']
                    if name_look == True and row['action'] == 'setMeta' and row['command'] == 'setName':
                        pp_name = row['value_to_set']
                        name_look = False

                counter = counter + create_count

                # build the lower-level Block
                instructions_list.extend(sub_block_rows)

                # now link it to a property
                part_dicts = cameo_part_prop_create_dicts(
                    name=pp_name[1:-1],
                    order_start=counter,
                    owner_obj=self_temp_var,
                    assoc_owner=owner_name,
                    type_ref=typ_ref
                )

                instructions_list.extend(part_dicts)

                counter = counter + 1

                # check for multiplicities
                if part in self.part_lower_mult_dict:
                    lower_val_dict = cameo_multval_create_dicts(
                        order_start=str(counter),
                        owner_obj='prop_id_' + str(counter - 1),
                        lit_type='Integer',
                        lit_val=str(self.part_lower_mult_dict[part]),
                        kind='Lower'
                    )

                    instructions_list.extend(lower_val_dict)

                    counter = counter + 1

                # check for multiplicities
                if part in self.part_upper_mult_dict:
                    if part in self.part_lower_mult_dict:
                        upper_val_dict = cameo_multval_create_dicts(
                            order_start=str(counter),
                            owner_obj='prop_id_' + str(counter - 2),
                            lit_type='Integer',
                            lit_val=str(self.part_upper_mult_dict[part]),
                            kind='Upper'
                        )
                    else:
                        upper_val_dict = cameo_multval_create_dicts(
                            order_start=str(counter),
                            owner_obj='prop_id_' + str(counter - 1),
                            lit_type='Integer',
                            lit_val=str(self.part_upper_mult_dict[part]),
                            kind='Upper'
                        )

                    instructions_list.extend(upper_val_dict)

                    counter = counter + 1

        except Exception:
            print('Error in part creation')
            raise

        return instructions_list

#################### SIMPLE SETS OF OPERATIONS #######################

def cameo_package_create_dicts(name='', order_start=0, owner_obj=''):
    ele_create = cameo_element_creation_dict(
        temp_var_name='pkg_id_' + str(order_start),
        factory_handle_name='myElementsFactory',
        meta_element='Package'
    )

    ele_rename = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Name',
        value='\"' + name + '\"'
    )

    ele_own = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Owner',
        value=owner_obj
    )

    strings = [];

    strings.append(
        ele_create
    )

    strings.append(
        ele_rename
    )

    strings.append(
        ele_own
    )

    return strings

def cameo_block_create_dicts(name='', temp_var_base='class_id_', order_start=0, owner_obj=''):
    ele_create = cameo_element_creation_dict(
        temp_var_name=temp_var_base + str(order_start),
        factory_handle_name='myElementsFactory',
        meta_element='Class'
    )

    ele_rename = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Name',
        value='\"' + name + '\"'
    )

    ele_own = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Owner',
        value=owner_obj
    )

    ele_stereo = cameo_apply_stereotype_dict(
        temp_var_name=ele_create['temp_var'],
        stereo_name='Block'
    )

    strings = []
    strings.append(
        ele_create
    )
    strings.append(
        ele_rename
    )
    strings.append(
        ele_own
    )
    strings.append(
        ele_stereo
    )

    return strings


def cameo_part_prop_create_dicts(name='',
                                 order_start=0,
                                 owner_obj='',
                                 assoc_owner='',
                                 type_ref=''):
    ele_create = cameo_element_creation_dict(
        temp_var_name='prop_id_' + str(order_start),
        factory_handle_name='myElementsFactory',
        meta_element='Property'
    )

    ele_rename = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Name',
        value='\"' + name + '\"'
    )

    ele_own = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Owner',
        value=owner_obj
    )

    ele_stereo = cameo_apply_stereotype_dict(
        temp_var_name=ele_create['temp_var'],
        stereo_name='PartProperty'
    )

    ele_type = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Type',
        value=type_ref
    )

    strings = []

    strings.append(
        ele_create
    )

    strings.append(
        ele_rename
    )

    strings.append(
        ele_own
    )

    strings.append(
        ele_stereo
    )

    strings.append(
        ele_type
    )

    return strings


def cameo_value_prop_create_dicts(name='', order_start=0, owner_obj='', val_type=''):
    ele_create = cameo_element_creation_dict(
        temp_var_name='prop_id_' + str(order_start),
        factory_handle_name='myElementsFactory',
        meta_element='Property'
    )

    ele_rename = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Name',
        value='\"' + name + '\"'
    )

    ele_own = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Owner',
        value=owner_obj
    )

    ele_stereo = cameo_apply_stereotype_dict(
        temp_var_name=ele_create['temp_var'],
        stereo_name='ValueProperty'
    )

    ele_type = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Type',
        value=val_type
    )

    strings = []

    strings.append(
        ele_create
    )

    strings.append(
        ele_rename
    )

    strings.append(
        ele_own
    )

    strings.append(
        ele_stereo
    )

    strings.append(
        ele_type
    )

    return strings


def cameo_literalval_create_dicts(order_start=0, owner_obj='', lit_type='Real', lit_val=''):
    ele_create = cameo_element_creation_dict(
        temp_var_name='val_id_' + str(order_start),
        factory_handle_name='myElementsFactory',
        meta_element='Literal' + lit_type
    )

    ele_own = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Owner',
        value=owner_obj
    )

    ele_dval = cameo_metaprop_single_set_dict(
        temp_var_name=owner_obj,
        meta_prop='DefaultValue',
        value=ele_create['temp_var']
    )

    ele_lval = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Value',
        value=lit_val
    )

    strings = []

    strings.append(
        ele_create
    )

    strings.append(
        ele_own
    )

    strings.append(
        ele_dval
    )

    strings.append(
        ele_lval
    )

    return strings


def cameo_multval_create_dicts(order_start=0, owner_obj='', lit_type='Real', lit_val='', kind=''):
    ele_create = cameo_element_creation_dict(
        temp_var_name='val_id_' + str(order_start),
        factory_handle_name='myElementsFactory',
        meta_element='Literal' + lit_type
    )

    ele_own = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Owner',
        value=owner_obj
    )

    ele_dval = cameo_metaprop_single_set_dict(
        temp_var_name=owner_obj,
        meta_prop=kind + 'Value',
        value=ele_create['temp_var']
    )

    ele_lval = cameo_metaprop_single_set_dict(
        temp_var_name=ele_create['temp_var'],
        meta_prop='Value',
        value=lit_val
    )

    strings = []

    strings.append(
        ele_create
    )

    strings.append(
        ele_own
    )

    strings.append(
        ele_dval
    )

    strings.append(
        ele_lval
    )

    return strings