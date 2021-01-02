import compound_cameo as MD_Cmp
import core_cameo_ops as MD_Ops

import uuid

class T_Component_Function():
    # Hybridizes EFFBD IDEF0 approach with
    # Yildirim et. al, "Function modeling using the system state flow diagram" and
    # a dash of JPL State Analysis

    def __init__(self, order):
        self.name = ''
        self.flow_outcome_name = None
        self.flow_outcome_type = None
        self.state_outcome_var = None
        self.state_outcome_name = None
        self.state_target = None
        self.inputs = []  # shows required inputs
        self.controls = []  # shows required manual control
        self.mechanisms = []
        self.order = order
        self.cameo_references = {}

    def generate_for_cameo_abstract(self, owner):

        instructions_list = []

        function_id = str(uuid.uuid4()).replace('-', '_')
        input_id = str(uuid.uuid4()).replace('-', '_')
        state_id = str(uuid.uuid4()).replace('-', '_')
        flow_para_id = str(uuid.uuid4()).replace('-', '_')

        # support object lookups for other connections
        self.cameo_references.update({'Function': 'function_id_' + function_id})
        self.cameo_references.update({'State Signal': 'signal_id_' + state_id})
        self.cameo_references.update({'State Target Parameter': 'parameter_id_' + input_id})
        self.cameo_references.update({'State Target Node': 'apn_id_' + input_id})
        self.cameo_references.update({'State Send Signal Action': 'ssa_id_' + state_id})
        self.cameo_references.update({'State SSA Pin': 'ssa_input_id_' + state_id})
        self.cameo_references.update({'Initial Node': 'initial_id_' + function_id})
        self.cameo_references.update({'Initial Control': 'initial_control_id_' + function_id})
        self.cameo_references.update({'Flow Parameter': 'flow_parameter_id_' + flow_para_id})

        function_create = MD_Cmp.cameo_element_creation_dict(
            temp_var_name='function_id_' + function_id,
            factory_handle_name='myElementsFactory',
            meta_element='Activity'
        )

        function_owner = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='function_id_' + function_id,
            meta_prop='Owner',
            value=owner
        )

        function_name = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='function_id_' + function_id,
            meta_prop='Name',
            value='\"' + self.name + '\"'
        )

        # need to condition this on state input

        if self.state_target is not None:
            signal_create = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='signal_id_' + state_id,
                factory_handle_name='myElementsFactory',
                meta_element='Signal'
            )

            signal_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='signal_id_' + state_id,
                meta_prop='Owner',
                value=owner
            )

            signal_name = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='signal_id_' + state_id,
                meta_prop='Name',
                value='\"' + self.state_outcome_name + '\"'
            )

            para = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='parameter_id_' + input_id,
                factory_handle_name='myElementsFactory',
                meta_element='Parameter'
            )

            para_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='parameter_id_' + input_id,
                meta_prop='Owner',
                value='function_id_' + function_id
            )

            para_name = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='parameter_id_' + input_id,
                meta_prop='Name',
                value='\"' + self.state_outcome_name + '\"'
            )

            para_type = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='parameter_id_' + input_id,
                meta_prop='Type',
                value=self.state_target
            )

            new_input_node = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='apn_id_' + input_id,
                factory_handle_name='myElementsFactory',
                meta_element='ActivityParameterNode'
            )

            new_input_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='apn_id_' + input_id,
                meta_prop='Owner',
                value='function_id_' + function_id
            )

            new_input_para = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='apn_id_' + input_id,
                meta_prop='Parameter',
                value='parameter_id_' + input_id
            )

            activity_input_node = MD_Ops.cameo_gather_items(
                temp_var_name='function_id_' + function_id,
                meta_prop='Node',
                return_value='activity_input_node_id_0',
                is_list=True
            )

            ssa_create = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='ssa_id_' + state_id,
                factory_handle_name='myElementsFactory',
                meta_element='SendSignalAction'
            )

            ssa_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='ssa_id_' + state_id,
                meta_prop='Owner',
                value='function_id_' + function_id
            )

            ssa_signal = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='ssa_id_' + state_id,
                meta_prop='Signal',
                value='signal_id_' + state_id
            )

            ssa_input_create = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='ssa_input_id_' + state_id,
                factory_handle_name='myElementsFactory',
                meta_element='InputPin'
            )

            ssa_input_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='ssa_input_id_' + state_id,
                meta_prop='Owner',
                value='ssa_id_' + state_id
            )

            ssa_input_name = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='ssa_input_id_' + state_id,
                meta_prop='Name',
                value='\"' + 'target' + '\"'
            )

            ssa_target = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='ssa_id_' + state_id,
                meta_prop='Target',
                value='ssa_input_id_' + state_id
            )

            initial_node_create = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='initial_id_' + function_id,
                factory_handle_name='myElementsFactory',
                meta_element='InitialNode'
            )

            initial_node_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='initial_id_' + function_id,
                meta_prop='Owner',
                value='function_id_' + function_id
            )

            initial_flow_create = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='initial_control_id_' + function_id,
                factory_handle_name='myElementsFactory',
                meta_element='ControlFlow'
            )

            initial_flow_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='initial_control_id_' + function_id,
                meta_prop='Owner',
                value='function_id_' + function_id
            )

            initial_flow_source = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='initial_control_id_' + function_id,
                meta_prop='Source',
                value='initial_id_' + function_id
            )

            initial_flow_target = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='initial_control_id_' + function_id,
                meta_prop='Target',
                value='ssa_id_' + state_id
            )

            target_to_sig = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='obj_flow_id_' + str(0),
                factory_handle_name='myElementsFactory',
                meta_element='ObjectFlow'
            )

            target_to_sig_owner = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(0),
                meta_prop='Owner',
                value='function_id_' + function_id
            )

            target_to_sig_source = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(0),
                meta_prop='Source',
                value='apn_id_' + input_id
            )

            target_to_sig_target = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='obj_flow_id_' + str(0),
                meta_prop='Target',
                value='ssa_input_id_' + state_id
            )

        if self.flow_outcome_type is not None:
            out_para = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='flow_parameter_id_' + flow_para_id,
                factory_handle_name='myElementsFactory',
                meta_element='Parameter'
            )

            out_para_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='flow_parameter_id_' + flow_para_id,
                meta_prop='Owner',
                value='function_id_' + function_id
            )

            out_para_name = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='flow_parameter_id_' + flow_para_id,
                meta_prop='Name',
                value='\"' + self.flow_outcome_name + '\"'
            )

            out_para_type = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='flow_parameter_id_' + flow_para_id,
                meta_prop='Type',
                value=self.flow_outcome_type
            )

            out_para_dir = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='flow_parameter_id_' + flow_para_id,
                meta_prop='Direction',
                value='com.nomagic.uml2.ext.magicdraw.classes.mdkernel.ParameterDirectionKindEnum.OUT'
            )

            new_output_node = MD_Cmp.cameo_element_creation_dict(
                temp_var_name='apn_id_' + flow_para_id,
                factory_handle_name='myElementsFactory',
                meta_element='ActivityParameterNode'
            )

            new_output_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='apn_id_' + flow_para_id,
                meta_prop='Owner',
                value='function_id_' + function_id
            )

            new_output_para = MD_Cmp.cameo_metaprop_single_set_dict(
                temp_var_name='apn_id_' + flow_para_id,
                meta_prop='Parameter',
                value='flow_parameter_id_' + flow_para_id
            )

        instructions_list.append(function_create)
        instructions_list.append(function_owner)
        instructions_list.append(function_name)

        if self.state_target is not None:
            instructions_list.append(signal_create)
            instructions_list.append(signal_owner)
            instructions_list.append(signal_name)
            instructions_list.append(para)
            instructions_list.append(para_ownership)
            instructions_list.append(para_name)
            instructions_list.append(para_type)
            instructions_list.append(new_input_node)
            instructions_list.append(new_input_ownership)
            instructions_list.append(new_input_para)
            # instructions_list.append(activity_input_node)
            instructions_list.append(ssa_create)
            instructions_list.append(ssa_owner)
            instructions_list.append(ssa_signal)
            instructions_list.append(ssa_input_create)
            instructions_list.append(ssa_input_owner)
            instructions_list.append(ssa_input_name)
            instructions_list.append(ssa_target)
            instructions_list.append(initial_node_create)
            instructions_list.append(initial_node_owner)
            instructions_list.append(initial_flow_create)
            instructions_list.append(initial_flow_owner)
            instructions_list.append(initial_flow_source)
            instructions_list.append(initial_flow_target)
            instructions_list.append(target_to_sig)
            instructions_list.append(target_to_sig_owner)
            instructions_list.append(target_to_sig_source)
            instructions_list.append(target_to_sig_target)

        if self.flow_outcome_type is not None:
            instructions_list.append(out_para)
            instructions_list.append(out_para_ownership)
            instructions_list.append(out_para_name)
            instructions_list.append(out_para_dir)
            instructions_list.append(out_para_type)
            instructions_list.append(new_output_node)
            instructions_list.append(new_output_ownership)
            instructions_list.append(new_output_para)

        return instructions_list


class T_Object_Nominal_State():
    # Represents a nominal state of something in the world such as
    # 'Archived' or 'In Transit' or 'At Destination'
    # Does not imply particular semantics, this is left to tool-specific
    # adaptations

    def __init__(self):
        self.name = ''
        self.transition_name = ''

        self.working_id = str(uuid.uuid4()).replace('-', '_')

    def generate_for_cameo_abstract(self, signal_owner_id, state_machine_owner_id):
        instructions_list = []

        signal = MD_Cmp.cameo_element_creation_dict(
            temp_var_name='signal_id_' + self.working_id,
            factory_handle_name='myElementsFactory',
            meta_element='Signal'
        )

        new_input_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='signal_id_' + self.working_id,
            meta_prop='Owner',
            value=signal_owner_id
        )

        new_input_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='signal_id_' + self.working_id,
            meta_prop='Name',
            value='\"' + self.transition_name + '\"'
        )

        signal = MD_Cmp.cameo_element_creation_dict(
            temp_var_name='state_id_' + self.working_id,
            factory_handle_name='myElementsFactory',
            meta_element='State'
        )

        new_input_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='state_id_' + self.working_id,
            meta_prop='Owner',
            value=state_machine_owner_id
        )

        new_input_ownership = MD_Cmp.cameo_metaprop_single_set_dict(
            temp_var_name='state_id_' + self.working_id,
            meta_prop='Name',
            value='\"' + self.name + '\"'
        )

        return instructions_list
