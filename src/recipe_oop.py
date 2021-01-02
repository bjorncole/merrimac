import compound_cameo as MD_Cmp
import core_cameo_ops as MD_Ops

import uuid

class T_Class(MD_Cmp.T_Sysml_Block):

    def __init__(self, order):
        super().__init__(order)
        self.methods = []

    def generate_cameo_handle(self):
        return 'class_id_' + self.working_id

    def generate_for_cameo_abstract(self, owner_name):

        instructions_list = []

        instructions_list.extend(
            super().generate_for_cameo_abstract(owner_name)
        )

        for method in self.methods:

            instructions_list.extend(
                method.generate_for_cameo_abstract(self.generate_cameo_handle())
            )
            #self.cameo_references.update({method.name: method.generate_cameo_handle()})

        return instructions_list

class T_Library_Class():

    def __init__(self):
        self.reference = ''
        self.name = ''

    def generate_cameo_handle(self):
        return self.reference

class T_Method_Signature():

    def __init__(self):

        self.name = ''
        self.implementation = None # Can be code block or short code block
        self.owning_class = None
        self.inputs = []
        self.return_val = None

        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_cameo_handle(self):

        return 'operation_id_' + self.working_id

    def generate_for_cameo_abstract(self, owner_name):

        instructions_list = []

        try:
            new_op = MD_Cmp.T_Sysml_Operation()
            new_op.working_id = self.working_id
            new_op.name = self.name
            if self.implementation is not None:
                new_op.method = self.implementation.generate_cameo_handle()
            self.owning_class.cameo_references.update(
                {
                    new_op.name: new_op.generate_cameo_handle()
                }
            )

            instructions_list.extend(
                new_op.generate_for_cameo_abstract(owner_name)
            )
        except AttributeError:
            if self.implementation is None:
                print(self.name + " has no implementation assigned!")
            if self.owning_class is None:
                print(self.name + " has no owning class assigned!")

        for para in self.inputs:

            instructions_list.extend(
                para.generate_for_cameo_abstract(self.generate_cameo_handle())
            )

        return instructions_list

class T_Object_Method_Call():

    # call a method on an object

    def __init__(self):
        self.method_to_call = None
        self.object_states_used = [] # this and the next list need to be in sync
        self.object_parameters_input = []

        self.cameo_references = {}

        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_cameo_handle(self):
        return 'coa_id_' + self.working_id

    def generate_for_cameo_abstract(self, owner):

        instructions_list = []

        caller = MD_Cmp.cameo_element_creation_dict(
            temp_var_name='coa_id_' + self.working_id,
            factory_handle_name='myElementsFactory',
            meta_element='CallOperationAction'
        )

        caller_owner = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='coa_id_' + self.working_id,
            meta_prop='Owner',
            value=owner
        )

        caller_behavior = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='coa_id_' + self.working_id,
            meta_prop='Operation',
            value=self.method_to_call.generate_cameo_handle()
        )

        instructions_list.append(caller)
        instructions_list.append(caller_owner)
        instructions_list.append(caller_behavior)

        for inp in self.method_to_call.implementation.passed_parameters:

            pin_id = 'pin_id_' + str(uuid.uuid4()).replace('-', '_')

            # try to make and assign pins

            new_inp_pin = MD_Cmp.cameo_element_creation_dict(
                temp_var_name=pin_id,
                factory_handle_name='myElementsFactory',
                meta_element='InputPin'
            )

            new_inp_owner = MD_Ops.cameo_metaprop_single_set_dict(
                temp_var_name=pin_id,
                meta_prop='Owner',
                value=self.generate_cameo_handle()
            )

            new_inp_sync = MD_Ops.cameo_metaprop_single_set_dict(
                temp_var_name=pin_id,
                meta_prop='SyncElement',
                value=inp.generate_cameo_handle()
            )

            self.cameo_references.update(
                {
                    inp.name : pin_id
                }
            )

            instructions_list.append(new_inp_pin)
            instructions_list.append(new_inp_owner)
            instructions_list.append(new_inp_sync)

        # generate pins and build object flow maps from object states to them

        print('cameo references')
        print(self.cameo_references)

        for indx, state in enumerate(self.object_states_used):

            inc_obj_edge_create = MD_Ops.cameo_element_creation_dict(
                temp_var_name='obj_flow_id_' + str(indx),
                factory_handle_name='myElementsFactory',
                meta_element='ObjectFlow'
            )

            inc_obj_edge_own = MD_Ops.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(indx),
                meta_prop='Owner',
                value=owner
            )

            inc_obj_edge_source = MD_Ops.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(indx),
                meta_prop='Source',
                value=state.generate_cameo_handle()
            )

            inc_obj_edge_target = MD_Ops.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(indx),
                meta_prop='Target',
                value=self.cameo_references[self.object_parameters_input[indx].name]
            )

            instructions_list.append(inc_obj_edge_create)
            instructions_list.append(inc_obj_edge_own)

            instructions_list.append(inc_obj_edge_source)
            instructions_list.append(inc_obj_edge_target)

        return instructions_list

    def generate_for_java_code(self):

        instructions_list = []

        return instructions_list


class T_Object_State():
    # Represents a specific state (time-slice) of a code object

    def __init__(self):
        self.object = None
        self.working_name = ''

        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_cameo_handle(self):
        return 'fn_id_' + self.working_id

    def generate_for_cameo_abstract(self, owner):
        instructions_list = []

        output_fork = MD_Cmp.cameo_element_creation_dict(
            temp_var_name='fn_id_' + self.working_id,
            factory_handle_name='myElementsFactory',
            meta_element='ForkNode'
        )

        fork_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='fn_id_' + self.working_id,
            meta_prop='Owner',
            value=owner
        )

        f_name = ''

        if self.working_name == '':
            f_name = self.object.name
        else:
            f_name = self.working_name

        fork_name = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='fn_id_' + self.working_id,
            meta_prop='Name',
            value='\"' + f_name + '\"'
        )

        instructions_list.append(output_fork)
        instructions_list.append(fork_ownership)
        instructions_list.append(fork_name)

        return instructions_list


class T_Object_State_Update():
    # Track the update of a state object and provide a handle to the
    # updated version

    def __init__(self):
        self.previous_object_state = None
        self.next_object_state = None
        self.attribute_to_update = None
        self.state_values_to_use = []  # this should be a list of object states
        self.update_kind = 'set'
        self.update_iteration = 0
        self.literal = False
        self.cameo_temp_var_dict = {}

    def generate_for_cameo_abstract(self, owner_val):
        instructions_list = []

        # make an incoming object flow to take in the object to update
        inc_obj_edge_create = MD_Ops.cameo_element_creation_dict(
            temp_var_name='obj_flow_id_' + str(0),
            factory_handle_name='myElementsFactory',
            meta_element='ObjectFlow'
        )

        inc_obj_edge_own = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='obj_flow_id_' + str(0),
            meta_prop='Owner',
            value=owner_val
        )

        # core add value action
        asfva_create = MD_Ops.cameo_element_creation_dict(
            temp_var_name='asfva_id_' + str(0),
            factory_handle_name='myElementsFactory',
            meta_element='AddStructuralFeatureValueAction'
        )

        asfva_own = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='asfva_id_' + str(0),
            meta_prop='Owner',
            value=owner_val
        )

        # create action will automatically have an object pin

        pin_fetch = MD_Ops.cameo_gather_items(
            temp_var_name='asfva_id_' + str(0),
            meta_prop='Input',
            return_value='obj_pin_id_0',
            is_list=True
        )

        inc_obj_edge_src = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='obj_flow_id_' + str(0),
            meta_prop='Source',
            value=self.previous_object_state.generate_cameo_handle()
        )

        inc_obj_edge_tgt = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='obj_flow_id_' + str(0),
            meta_prop='Target',
            value='obj_pin_id_0'
        )

        # core add value action
        asfva_input_create = MD_Ops.cameo_element_creation_dict(
            temp_var_name='asfva_value_id_' + str(0),
            factory_handle_name='myElementsFactory',
            meta_element='InputPin'
        )

        asfva_input_own = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='asfva_value_id_' + str(0),
            meta_prop='Owner',
            value='asfva_id_' + str(0)
        )

        asfva_input_name = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='asfva_value_id_' + str(0),
            meta_prop='Name',
            value='\"value\"'
        )

        # work with incoming value

        vals = []

        for state_val in self.state_values_to_use:
            inc_val_edge_create = MD_Ops.cameo_element_creation_dict(
                temp_var_name='obj_flow_id_' + str(2),
                factory_handle_name='myElementsFactory',
                meta_element='ObjectFlow'
            )

            inc_val_edge_own = MD_Ops.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(2),
                meta_prop='Owner',
                value=owner_val
            )

            inc_val_edge_src = MD_Ops.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(2),
                meta_prop='Source',
                value=state_val.generate_cameo_handle()
            )

            inc_val_edge_tgt = MD_Ops.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(2),
                meta_prop='Target',
                value='asfva_value_id_' + str(0)
            )

            vals.append(inc_val_edge_create)
            vals.append(inc_val_edge_own)
            vals.append(inc_val_edge_src)
            vals.append(inc_val_edge_tgt)

        # results pin

        asfva_result_create = MD_Ops.cameo_element_creation_dict(
            temp_var_name='asfva_result_id_' + str(0),
            factory_handle_name='myElementsFactory',
            meta_element='OutputPin'
        )

        asfva_result_own = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='asfva_result_id_' + str(0),
            meta_prop='Owner',
            value='asfva_id_' + str(0)
        )

        asfva_result_name = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='asfva_result_id_' + str(0),
            meta_prop='Name',
            value='\"result\"'
        )

        out_obj_edge_create = MD_Ops.cameo_element_creation_dict(
            temp_var_name='obj_flow_id_' + str(1),
            factory_handle_name='myElementsFactory',
            meta_element='ObjectFlow'
        )

        out_obj_edge_own = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='obj_flow_id_' + str(1),
            meta_prop='Owner',
            value=owner_val
        )

        out_obj_edge_src = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='obj_flow_id_' + str(1),
            meta_prop='Source',
            value='asfva_result_id_' + str(0),
        )

        out_obj_edge_tgt = MD_Ops.cameo_metaprop_single_set_dict(
            temp_var_name='obj_flow_id_' + str(1),
            meta_prop='Target',
            value=self.next_object_state.generate_cameo_handle()
        )

        instructions_list.append(inc_obj_edge_create)
        instructions_list.append(inc_obj_edge_own)
        instructions_list.append(asfva_create)
        instructions_list.append(asfva_own)
        instructions_list.append(pin_fetch)
        instructions_list.append(inc_obj_edge_src)
        instructions_list.append(inc_obj_edge_tgt)
        instructions_list.append(asfva_input_create)
        instructions_list.append(asfva_input_own)
        instructions_list.append(asfva_input_name)
        instructions_list.append(asfva_result_create)
        instructions_list.append(asfva_result_own)
        instructions_list.append(asfva_result_name)

        instructions_list.extend(
            self.next_object_state.generate_for_cameo_abstract(owner_val))

        instructions_list.append(out_obj_edge_create)
        instructions_list.append(out_obj_edge_own)
        instructions_list.append(out_obj_edge_src)
        instructions_list.append(out_obj_edge_tgt)

        for val in vals:
            instructions_list.append(val)

        return instructions_list

    def generate_for_java_code(self):

        instructions_list = []

        return instructions_list


class T_Code_Input():

    def __init__(self):
        self.name = ''
        self.para_type = None
        self.single_item = True

        self.working_id = str(uuid.uuid4()).replace('-', '_')
        self.generated_id = ''

    def generate_cameo_handle(self):
        if self.generated_id == '':
            return 'parameter_id_' + self.working_id
        else:
            return self.generated_id

    def generate_for_cameo_abstract(self, owner):

        instructions_list = []

        para_type = ''

        if isinstance(self.para_type, str):
            para_type = self.para_type
        else:
            para_type = self.para_type.generate_cameo_handle()


        new_para = MD_Cmp.T_Sysml_Parameter()
        new_para.name = self.name
        new_para.type = para_type
        self.generated_id = new_para.generate_cameo_handle()
        new_para.direction = 'in'
        if self.single_item:
            new_para.lower = 1
            new_para.upper = 1
        else:
            new_para.lower = 0
            new_para.upper = -1

        new_para_instructions = new_para.generate_for_cameo_abstract(owner)

        instructions_list.extend(new_para_instructions)

        return instructions_list

class T_Short_Code_Block(MD_Cmp.T_Sysml_Opaque_Behavior):

    # A code block with non-modeled content

    pass

class T_Code_Block():
    def __init__(self):
        self.name = ''
        self.variable_changes = {}  # track variable handles for later processing
        self.object_state_updates = []  # changes to states
        self.object_creations = []  # creation of objects
        self.passed_parameter_dict = {}  # parameter names to types
        self.passed_parameter_state_dict = {}  # parameter names to initial object states
        self.function_calls = []  # call naked subroutines - expect Code Blocks
        self.method_calls = []  # call methods of classes
        self.passed_parameters = [] # input parameters

        self.ordering = []  # orders the above

        self.cameo_temp_var_dict = {}

        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_cameo_handle(self):
        return 'activity_id_' + self.working_id

    def generate_for_cameo_sig_only(self, owner_val):
        # build only activity and parameters, no internals
        instructions_list = []

        # create the activity to represent the block

        activity_wrapper = MD_Cmp.cameo_element_creation_dict(
            temp_var_name='activity_id_' + self.working_id,
            factory_handle_name='myElementsFactory',
            meta_element='Activity'
        )

        activity_owner = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='activity_id_' + self.working_id,
            meta_prop='Owner',
            value=owner_val
        )

        activity_name = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='activity_id_' + self.working_id,
            meta_prop='Name',
            value='\"' + self.name + '\"'
        )

        # make incoming objects

        instructions_list.append(activity_wrapper)
        instructions_list.append(activity_owner)
        instructions_list.append(activity_name)

        # fill in incoming variables

        for para_name, para_type in self.passed_parameter_dict.items():
            # need to map parameter names to objects for later object flows

            working_para = MD_Cmp.T_Sysml_Parameter()
            working_para.direction = 'in'
            working_para.name = para_name
            if para_type is not None:
                if isinstance(para_type, str):
                    working_para.type = para_type
                else:
                    working_para.type = para_type.generate_cameo_handle()

            instructions_list.extend(
                working_para.generate_for_cameo_abstract('activity_id_' + self.working_id))

            instructions_list.extend(
                self.passed_parameter_state_dict[para_name]. \
                    generate_for_cameo_abstract('activity_id_' + self.working_id)
            )

            # object flow for input to initial states

            new_para_node = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='apn_id_' + working_para.generate_cameo_handle(),
                factory_handle_name='myElementsFactory',
                meta_element='ActivityParameterNode'
            )

            new_para_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='apn_id_' + working_para.generate_cameo_handle(),
                meta_prop='Owner',
                value='activity_id_' + self.working_id
            )

            assign_para_node = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='apn_id_' + working_para.generate_cameo_handle(),
                meta_prop='Parameter',
                value=working_para.generate_cameo_handle()
            )

            target_to_sig = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='obj_flow_id_' + working_para.generate_cameo_handle(),
                factory_handle_name='myElementsFactory',
                meta_element='ObjectFlow'
            )

            target_to_sig_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + working_para.generate_cameo_handle(),
                meta_prop='Owner',
                value='activity_id_' + self.working_id
            )

            target_to_sig_source = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + working_para.generate_cameo_handle(),
                meta_prop='Source',
                value='apn_id_' + working_para.generate_cameo_handle()
            )

            target_to_sig_target = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + working_para.generate_cameo_handle(),
                meta_prop='Target',
                value=self.passed_parameter_state_dict[para_name].generate_cameo_handle()
            )

            instructions_list.append(new_para_node)
            instructions_list.append(new_para_ownership)
            instructions_list.append(assign_para_node)
            instructions_list.append(target_to_sig)
            instructions_list.append(target_to_sig_owner)
            instructions_list.append(target_to_sig_source)
            instructions_list.append(target_to_sig_target)

        for para in self.passed_parameters:

            instructions_list.extend(
                self.passed_parameter_state_dict[para.name]. \
                    generate_for_cameo_abstract('activity_id_' + self.working_id)
            )

            instructions_list.extend(
                para.generate_for_cameo_abstract(self.generate_cameo_handle())
            )

            # object flow for input to initial states

            new_para_node = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='apn_id_' + para.generate_cameo_handle(),
                factory_handle_name='myElementsFactory',
                meta_element='ActivityParameterNode'
            )

            new_para_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='apn_id_' + para.generate_cameo_handle(),
                meta_prop='Owner',
                value='activity_id_' + self.working_id
            )

            assign_para_node = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='apn_id_' + para.generate_cameo_handle(),
                meta_prop='Parameter',
                value=para.generate_cameo_handle()
            )

            target_to_sig = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='obj_flow_id_' + para.generate_cameo_handle(),
                factory_handle_name='myElementsFactory',
                meta_element='ObjectFlow'
            )

            target_to_sig_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + para.generate_cameo_handle(),
                meta_prop='Owner',
                value='activity_id_' + self.working_id
            )

            target_to_sig_source = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + para.generate_cameo_handle(),
                meta_prop='Source',
                value='apn_id_' + para.generate_cameo_handle()
            )

            target_to_sig_target = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + para.generate_cameo_handle(),
                meta_prop='Target',
                value=self.passed_parameter_state_dict[para.name].generate_cameo_handle()
            )

            instructions_list.append(new_para_node)
            instructions_list.append(new_para_ownership)
            instructions_list.append(assign_para_node)
            instructions_list.append(target_to_sig)
            instructions_list.append(target_to_sig_owner)
            instructions_list.append(target_to_sig_source)
            instructions_list.append(target_to_sig_target)

        return instructions_list

    def generate_for_cameo_internals_only(self, owner_val):

        instructions_list = []

        # fill in the object changes

        for indx, obj_state in enumerate(self.object_state_updates):
            # expand the individual list of updates

            update_dicts = obj_state.generate_for_cameo_abstract('activity_id_' + self.working_id)

            instructions_list.extend(update_dicts)

            # add general function calls

        for indx, method in enumerate(self.function_calls):
            method_line = ''

            if isinstance(method, str):
                method_line = method
            else:
                method_line = method.generate_cameo_handle()

            caller = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='cba_id_' + method_line,
                factory_handle_name='myElementsFactory',
                meta_element='CallBehaviorAction'
            )

            caller_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='cba_id_' + method_line,
                meta_prop='Owner',
                value='activity_id_' + self.working_id
            )

            caller_behavior = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='cba_id_' + method_line,
                meta_prop='Behavior',
                value=method_line
            )

            instructions_list.append(caller)
            instructions_list.append(caller_owner)
            instructions_list.append(caller_behavior)

        # add method calls

        for indx, method in enumerate(self.method_calls):

            instructions_list.extend(
                method.generate_for_cameo_abstract(
                    self.generate_cameo_handle()
                )
            )

        return instructions_list

    def generate_for_cameo_abstract(self, owner_val):

        instructions_list = []

        instructions_list.extend(
            self.generate_for_cameo_sig_only(owner_val)
        )

        instructions_list.extend(
            self.generate_for_cameo_internals_only(owner_val)
        )

        return instructions_list