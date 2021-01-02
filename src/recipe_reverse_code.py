import compound_cameo as MD_Cmp
import core_cameo_ops as MD_Ops

import recipe_oop as RC_OOP

import javalang
import uuid

def oop_objects_from_method_sig(signature='', is_opaque=True, types=[]):
    tree = javalang.parse.parse(signature)

    parameter_names = [para.name for para in tree.types[0].body[0].parameters]
    parameter_types = [para.type.name for para in tree.types[0].body[0].parameters]

    sig_dict = {}

    print("Signature tree is " + str(tree))

    # if opaque, use Short Code Block, otherwise a Code Block

    inputs = []

    sig_obj = RC_OOP.T_Method_Signature()
    sig_obj.name = tree.types[0].body[0].name

    for indx, para in enumerate(parameter_names):
        new_input = RC_OOP.T_Code_Input()
        new_input.name = para
        new_input.single_item = True
        for typ in types:
            if parameter_types[indx] == typ.name:
                new_input.para_type = typ

        inputs.append(new_input)
        sig_obj.inputs.append(new_input)

    sig_dict.update(
        {
            tree.types[0].body[0].name: sig_obj
        }
    )

    return sig_dict