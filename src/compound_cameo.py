from core_cameo_ops import *
from core_cameo_commands import *

import uuid

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

        # attributes here are literal values
        self.attributes_dict = {}
        self.att_types_dict = {}
        self.att_littypes_dict = {}
        self.part_lower_mult_dict = {}
        self.part_upper_mult_dict = {}
        # parts go to local types
        self.part_types_dict = {}
        self.ref_lower_mult_dict = {}
        self.ref_upper_mult_dict = {}
        # references are passed handles to types
        self.ref_types_dict = {}
        # operations are passed handles to methods
        self.operation_methods_dict = {}
        self.order = order
        self.general_types = []

        self.meta = 'Block'

        self.cameo_references = {}

        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_cameo_handle(self):
        return 'class_id_' + self.working_id

    def generate_for_cameo_abstract(self, owner_name):
        instructions_list = []

        self_temp_var = ''
        try:
            self_temp_var = 'class_id_' + self.working_id
            instructions_list.extend(cameo_block_create_dicts(
                name=self.attributes_dict['name'],
                temp_var='class_id_' + self.working_id,
                owner_obj=owner_name,
                meta=self.meta
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
                            owner_obj='class_id_' + self.working_id,
                            val_type=self.att_types_dict[non_name]
                        )

                    counter = counter + 1

                    instructions_list.extend(new_dicts)

                    val_dicts = \
                        cameo_literalval_create_dicts(
                            order_start=str(counter),
                            owner_obj='prop_id_' + str(counter - 1),
                            lit_type=self.att_littypes_dict[non_name],
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

            for ref, typ in self.ref_types_dict.items():

                ref_id = 'ref_id_' + str(uuid.uuid4()).replace('-', '_')

                ref_prop = cameo_element_creation_dict(
                    temp_var_name=ref_id,
                    factory_handle_name='myElementsFactory',
                    meta_element='Property'
                )

                ref_stereo = cameo_apply_stereotype_dict(
                    temp_var_name=ref_id,
                    stereo_name='ReferenceProperty'
                )

                ref_prop_ownership = cameo_metaprop_single_set_dict(
                    temp_var_name=ref_id,
                    meta_prop='Owner',
                    value=self.generate_cameo_handle()
                )

                ref_prop_name = cameo_metaprop_single_set_dict(
                    temp_var_name=ref_id,
                    meta_prop='Name',
                    value='\"' + ref + '\"'
                )

                ref_prop_type = cameo_metaprop_single_set_dict(
                    temp_var_name=ref_id,
                    meta_prop='Type',
                    value=typ
                )

                instructions_list.append(ref_prop)
                instructions_list.append(ref_stereo)
                instructions_list.append(ref_prop_ownership)
                instructions_list.append(ref_prop_name)
                instructions_list.append(ref_prop_type)


        except Exception:
            print('Error in part creation')
            raise

        try:
            for sig, method in self.operation_methods_dict.items():
                if sig not in self.cameo_references:

                    new_op = T_Sysml_Operation()
                    new_op.name = sig
                    new_op.method = method
                    self.cameo_references.update(
                        {
                            sig: new_op.generate_cameo_handle()
                         }
                    )

                    # do name matching in operations for more general Blocks

                    instructions_list.extend(
                        new_op.generate_for_cameo_abstract('class_id_' + self.working_id))

                for gen in self.general_types:
                    for sig_gen, method_gen in gen.operation_methods_dict.items():
                        if sig_gen == sig:
                            new_op.redefined.append(
                                gen.cameo_references[sig_gen]
                            )

        except Exception:
            print('Error in operation creation')

        try:
            for gen in self.general_types:
                #create and own Generalizations

                gen_id = str(uuid.uuid4()).replace('-', '_')

                new_gen = cameo_element_creation_dict(
                    temp_var_name='general_id_' + gen_id,
                    factory_handle_name='myElementsFactory',
                    meta_element='Generalization'
                )

                gen_source = cameo_metaprop_single_set_dict(
                    temp_var_name='general_id_' + gen_id,
                    meta_prop='Specific',
                    value=self.generate_cameo_handle()
                )

                gen_target = cameo_metaprop_single_set_dict(
                    temp_var_name='general_id_' + gen_id,
                    meta_prop='General',
                    value=gen.generate_cameo_handle()
                )

                gen_owner = cameo_metaprop_single_set_dict(
                    temp_var_name='general_id_' + gen_id,
                    meta_prop='Owner',
                    value=self.generate_cameo_handle()
                )

                instructions_list.append(new_gen)
                instructions_list.append(gen_source)
                instructions_list.append(gen_target)
                instructions_list.append(gen_owner)

        except Exception:
            print('Error in generalization creation')

        return instructions_list

    @property
    def name(self):
        return self.attributes_dict['name']

    @name.setter
    def name(self, value):
        self.attributes_dict.update({'name': value})


class T_Sysml_Interface_Block(T_Sysml_Block):
    def __init__(self, order):
        super().__init__(order)

        self.meta = 'InterfaceBlock'

class T_Sysml_Parameter():
    def __init__(self):
        self.name = ''
        self.type = None
        self.direction = ''
        self.lower = 1
        self.upper = 1

        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_cameo_handle(self):
        return 'parameter_id_' + self.working_id

    def generate_for_cameo_abstract(self, owner):
        instructions_list = []

        para = cameo_element_creation_dict(
            temp_var_name='parameter_id_' + self.working_id,
            factory_handle_name='myElementsFactory',
            meta_element='Parameter'
        )

        para_ownership = cameo_metaprop_single_set_dict(
            temp_var_name='parameter_id_' + self.working_id,
            meta_prop='Owner',
            value=owner
        )

        para_name = cameo_metaprop_single_set_dict(
            temp_var_name='parameter_id_' + self.working_id,
            meta_prop='Name',
            value='\"' + self.name + '\"'
        )

        para_dir = cameo_metaprop_single_set_dict(
            temp_var_name='parameter_id_' + self.working_id,
            meta_prop='Direction',
            value='com.nomagic.uml2.ext.magicdraw.classes.mdkernel.' + \
                  'ParameterDirectionKindEnum.' + self.direction.upper()
        )

        lower_val_dict = cameo_multval_create_dicts(
            order_start=1,
            owner_obj='parameter_id_' + self.working_id,
            lit_type='Integer',
            lit_val=str(self.lower),
            kind='Lower'
        )

        upper_val_dict = cameo_multval_create_dicts(
            order_start=1,
            owner_obj='parameter_id_' + self.working_id,
            lit_type='UnlimitedNatural',
            lit_val=str(self.upper),
            kind='Upper'
        )

        instructions_list.append(para)
        instructions_list.append(para_ownership)
        instructions_list.append(para_name)
        instructions_list.append(para_dir)
        instructions_list.extend(lower_val_dict)
        instructions_list.extend(upper_val_dict)

        if self.type is not None:
            para_type = cameo_metaprop_single_set_dict(
                temp_var_name='parameter_id_' + self.working_id,
                meta_prop='Type',
                value=self.type
            )
            instructions_list.append(para_type)

        return instructions_list


class T_Sysml_Operation():
    def __init__(self):
        self.name = ''
        self.method = None
        self.redefined = []

        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_cameo_handle(self):
        return 'operation_id_' + self.working_id

    def generate_for_cameo_abstract(self, owner):
        instructions_list = []

        # make an incoming object flow to take in the object to update
        oper_create = cameo_element_creation_dict(
            temp_var_name=self.generate_cameo_handle(),
            factory_handle_name='myElementsFactory',
            meta_element='Operation'
        )

        oper_own = cameo_metaprop_single_set_dict(
            temp_var_name=self.generate_cameo_handle(),
            meta_prop='Owner',
            value=owner
        )

        oper_name = cameo_metaprop_single_set_dict(
            temp_var_name=self.generate_cameo_handle(),
            meta_prop='Name',
            value='\"' + self.name + '\"'
        )

        instructions_list.append(oper_create)
        instructions_list.append(oper_own)
        instructions_list.append(oper_name)

        if self.method is not None:

            oper_method = cameo_metaprop_list_set_dict(
                temp_var_name=self.generate_cameo_handle(),
                meta_prop='Method',
                value='[' + self.method + ']'
            )

            instructions_list.append(oper_method)

        redefined_str = '['

        for indx, redef in enumerate(self.redefined):
            if indx == 0:
                redefined_str = redefined_str + redef
            else:
                redefined_str = redefined_str + ',' + redef

        redefined_str = redefined_str + ']'


        if len(self.redefined) > 0:
            oper_redef = cameo_metaprop_list_set_dict(
                temp_var_name=self.generate_cameo_handle(),
                meta_prop='RedefinedOperation',
                value=redefined_str
            )
            instructions_list.append(oper_redef)

        return instructions_list


class T_Sysml_Opaque_Behavior():
    def __init__(self):
        self.parameters_dict = {}
        self.parameter_types_dict = {}
        self.parameter_directions_dict = {}
        self.paramter_lower_mults_dict = {}
        self.paramter_upper_mults_dict = {}
        self.body = ''
        self.name = ''
        self.language = ''
        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_cameo_handle(self):
        return 'opaque_id_' + self.working_id

    def generate_for_cameo_abstract(self, owner):
        instructions_list = []

        opaque = cameo_element_creation_dict(
            temp_var_name='opaque_id_' + self.working_id,
            factory_handle_name='myElementsFactory',
            meta_element='OpaqueBehavior'
        )

        opaque_ownership = cameo_metaprop_single_set_dict(
            temp_var_name='opaque_id_' + self.working_id,
            meta_prop='Owner',
            value=owner
        )

        opaque_name = cameo_metaprop_single_set_dict(
            temp_var_name='opaque_id_' + self.working_id,
            meta_prop='Name',
            value='\"' + self.name + '\"'
        )

        opaque_body = cameo_metaprop_list_set_dict(
            temp_var_name='opaque_id_' + self.working_id,
            meta_prop='Body',
            value='[\"' + self.body + '\"]'
        )

        opaque_language = cameo_metaprop_list_set_dict(
            temp_var_name='opaque_id_' + self.working_id,
            meta_prop='Language',
            value='[\"' + self.language + '\"]'
        )

        instructions_list.append(opaque)
        instructions_list.append(opaque_ownership)
        instructions_list.append(opaque_name)
        instructions_list.append(opaque_body)
        instructions_list.append(opaque_language)

        for k, para in self.parameters_dict.items():
            new_para = T_Sysml_Parameter()

            try:
                new_para.name = k
                new_para.type = self.parameter_types_dict[k]
                new_para.direction = self.parameter_directions_dict[k]
                new_para.lower = self.paramter_lower_mults_dict[k]
                new_para.upper = self.paramter_upper_mults_dict[k]
            except KeyError:
                pass

            new_para_instructions = new_para.generate_for_cameo_abstract(
                'opaque_id_' + self.working_id)

            instructions_list.extend(new_para_instructions)

        return instructions_list

class T_Sysml_Activity():
    def __init__(self):
        self.call_behaviors_dict = []
        self.call_behavior_behaviors_dict = []

class T_Sysml_Signal():
    def __init__(self):
        self.name = ''
        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_for_cameo_abstract(self, owner=None):
        instructions_list = []

        signal = cameo_element_creation_dict(
            temp_var_name='signal_id_' + self.working_id,
            factory_handle_name='myElementsFactory',
            meta_element='Signal'
        )

        signal_ownership = cameo_metaprop_single_set_dict(
            temp_var_name='signal_id_' + self.working_id,
            meta_prop='Owner',
            value=self.owner
        )

        signal_name = cameo_metaprop_single_set_dict(
            temp_var_name='signal_id_' + self.working_id,
            meta_prop='Name',
            value='\"' + self.name + '\"'
        )

        instructions_list.append(signal)
        instructions_list.append(signal_ownership)
        instructions_list.append(signal_name)

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

def cameo_block_create_dicts(name='', temp_var='class_id_', owner_obj='', meta='Block'):
    ele_create = cameo_element_creation_dict(
        temp_var_name=temp_var,
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
        stereo_name=meta
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
