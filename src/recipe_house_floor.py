import compound_cameo as MD_Cmp

import compound_freecad as FC_Cmp
import core_freecad_ops as FC_Ops

import math
import copy

class T_Housing_Board(MD_Cmp.T_Sysml_Block, FC_Cmp.T_Geom_Rect_Prism):

    def __init__(self, order):
        super().__init__(order)

    @property
    def name(self):
        try:
            return self.attributes_dict['name']
        except:
            return ''

    @name.setter
    def name(self, value):
        self.attributes_dict.update({'name': value})
        self.b_name = value.replace(" ", "_")

    @property
    def width(self):
        try:
            return self.attributes_dict['width']
        except:
            return ''

    @width.setter
    def width(self, value):
        self.attributes_dict.update({'width': value})
        self.att_types_dict.update({'width': 'Real'})
        self.p_height = value

    @property
    def thickness(self):
        try:
            return self.attributes_dict['thickness']
        except:
            return ''

    @thickness.setter
    def thickness(self, value):
        self.attributes_dict.update({'thickness': value})
        self.att_types_dict.update({'thickness': 'Real'})
        self.p_width = value

    @property
    def length(self):
        try:
            return self.attributes_dict['length']
        except:
            return ''

    @length.setter
    def length(self, value):
        self.attributes_dict.update({'length': value})
        self.att_types_dict.update({'length': 'Real'})
        self.p_length = value


class T_Housing_Panel(MD_Cmp.T_Sysml_Block, FC_Cmp.T_Geom_Rect_Prism):
    def __init__(self, order):
        super().__init__(order)

    @property
    def name(self):
        try:
            return self.attributes_dict['name']
        except:
            return ''

    @name.setter
    def name(self, value):
        self.attributes_dict.update({'name': value})
        self.b_name = value.replace(" ", "_")

    @property
    def width(self):
        try:
            return self.attributes_dict['width']
        except:
            return ''

    @width.setter
    def width(self, value):
        self.attributes_dict.update({'width': value})
        self.att_types_dict.update({'width': 'Real'})
        self.p_width = value

    @property
    def thickness(self):
        try:
            return self.attributes_dict['thickness']
        except:
            return ''

    @thickness.setter
    def thickness(self, value):
        self.attributes_dict.update({'thickness': value})
        self.att_types_dict.update({'thickness': 'Real'})
        self.p_length = value

    @property
    def depth(self):
        try:
            return self.attributes_dict['depth']
        except:
            return ''

    @depth.setter
    def depth(self, value):
        self.attributes_dict.update({'depth': value})
        self.att_types_dict.update({'depth': 'Real'})
        self.p_height = value


class T_Housing_Flooring_Frame(MD_Cmp.T_Sysml_Block, FC_Cmp.T_Geom_Assembly):
    def __init__(self, order):
        super().__init__(order)
        self.boards_wide = 0
        self.boards_deep = 0
        self.panels_across = 0
        self.panels_down = 0
        self.push_indx = 0
        self.final_indx = 0

    @property
    def name(self):
        try:
            return self.attributes_dict['name']
        except:
            return ''

    @name.setter
    def name(self, value):
        self.attributes_dict.update({'name': value})

    @property
    def base_width(self):
        try:
            return self.attributes_dict['base_width']
        except:
            return ''

    @base_width.setter
    def base_width(self, value):
        val_base = value / 16.0
        val_flush = round(val_base, 0) * 16.0
        self.boards_wide = math.floor(val_flush / 16.0)
        self.attributes_dict.update({'base_width': val_flush})
        self.att_types_dict.update({'base_width': 'Real'})

    @property
    def base_depth(self):
        try:
            return self.attributes_dict['base_depth']
        except:
            return ''

    @base_depth.setter
    def base_depth(self, value):
        # round to the nearest 16"
        val_base = value / 16.0
        val_flush = round(val_base, 0) * 16.0
        self.boards_deep = math.floor(val_flush / 16.0) + 1
        self.attributes_dict.update({'base_depth': val_flush})
        self.att_types_dict.update({'base_depth': 'Real'})

    @property
    def sill_board_kind(self):
        try:
            return self.part_types_dict['Sill Plate']
        except:
            return ''

    @sill_board_kind.setter
    def sill_board_kind(self, board_obj):
        self.part_types_dict.update({'Sill Plate': board_obj})

    @property
    def girder_board_kind(self):
        try:
            return self.part_types_dict['Girder']
        except:
            return ''

    @girder_board_kind.setter
    def girder_board_kind(self, board_obj):
        self.part_types_dict.update({'Girder': board_obj})
        self.part_lower_mult_dict.update({'Girder': self.boards_wide})
        self.part_upper_mult_dict.update({'Girder': self.boards_wide})

    @property
    def joist_board_kind(self):
        try:
            return self.part_types_dict['Joist']
        except:
            return ''

    @joist_board_kind.setter
    def joist_board_kind(self, board_obj):
        self.part_types_dict.update({'Joist': board_obj})
        self.part_lower_mult_dict.update({'Joist': self.boards_deep})
        self.part_upper_mult_dict.update({'Joist': self.boards_deep})

    @property
    def header_joist_board_kind(self):
        try:
            return self.part_types_dict['Header Joist']
        except:
            return ''

    @header_joist_board_kind.setter
    def header_joist_board_kind(self, board_obj):
        self.part_types_dict.update({'Header Joist': board_obj})
        self.part_lower_mult_dict.update({'Header Joist': 2})
        self.part_upper_mult_dict.update({'Header Joist': 2})

    @property
    def floor_board_kind(self):
        try:
            return self.part_types_dict['Floor Board']
        except:
            return ''

    @floor_board_kind.setter
    def floor_board_kind(self, board_obj):
        self.part_types_dict.update({'Floor Board': board_obj})

    def generate_for_freecad(self):
        # instructions_list = super().generate_for_freecad()

        instructions_list = []

        # make attach point local coordinate systems - one at +1/2Y and one at -1/2X

        lcs_count = 1

        self.floor_board_kind.p_plane = 'XY_Plane'

        # set up joists and girders

        for wide_pos in range(0, self.boards_wide):
            mod = ''
            if lcs_count - 1 > 99:
                mod = str(lcs_count - 1)
            elif lcs_count - 1 > 9:
                mod = '0' + str(lcs_count - 1)
            elif lcs_count - 1 > 0:
                mod = '00' + str(lcs_count - 1)

            new_girder = copy.deepcopy(self.girder_board_kind)
            new_girder.b_name = self.girder_board_kind.b_name + '_' + str(lcs_count)
            new_girder.p_plane = 'XZ_Plane' + mod

            for instr in new_girder.generate_for_freecad():
                instructions_list.append(instr)

            x = -self.attributes_dict['base_width'] / 2.0 + wide_pos * 16.0 + 8.0
            y = self.attributes_dict['base_depth'] / 2.0
            # new_lcs = freecad_exec_gui_command(command='Asm4_newLCS')

            lcs_place = 'App.Placement(App.Vector(' + \
                        str(x) + ',' + str(y) + ',0),App.Rotation(App.Vector(0,0,1),0))'

            lcs_pos = FC_Ops.freecad_set_document_field_dict(
                obj='Girder_' + str(lcs_count),
                att='Placement',
                value=lcs_place
            )
            # instructions_list.append(new_lcs)
            instructions_list.append(lcs_pos)

            lcs_count = lcs_count + 1

        for deep_pos in range(0, self.boards_deep):
            mod = ''
            if lcs_count - 1 > 99:
                mod = str(lcs_count - 1)
            elif lcs_count - 1 > 9:
                mod = '0' + str(lcs_count - 1)
            elif lcs_count - 1 > 0:
                mod = '00' + str(lcs_count - 1)

            new_joist = copy.deepcopy(self.joist_board_kind)
            new_joist.b_name = self.joist_board_kind.b_name + '_' + str(deep_pos)
            new_joist.p_plane = 'YZ_Plane' + mod

            for instr in new_joist.generate_for_freecad():
                instructions_list.append(instr)

            y_cheat = 0.0

            if deep_pos == self.boards_deep - 1:
                y_cheat = -self.joist_board_kind.thickness / 2.0

            if deep_pos == 0:
                y_cheat = self.joist_board_kind.thickness / 2.0

            x = -self.attributes_dict['base_width'] / 2.0 + self.joist_board_kind.thickness
            y = -self.attributes_dict['base_depth'] / 2.0 + deep_pos * 16.0 + \
                y_cheat
            # new_lcs = freecad_exec_gui_command(command='Asm4_newLCS')

            lift = self.girder_board_kind.width / 2.0 + \
                   self.joist_board_kind.width / 2.0

            lcs_place = 'App.Placement(App.Vector(' + \
                        str(x) + ',' + str(y) + ',' + str(lift) + '),App.Rotation(App.Vector(0,0,1),0))'

            lcs_pos = FC_Ops.freecad_set_document_field_dict(
                obj='Joist_' + str(deep_pos),
                att='Placement',
                value=lcs_place
            )

            # instructions_list.append(new_lcs)
            instructions_list.append(lcs_pos)

            lcs_count = lcs_count + 1

        # add the subfloor panels

        for across_pos in range(0, self.panels_across):
            for down_pos in range(0, self.panels_down):
                mod = ''

                if lcs_count - 1 > 99:
                    mod = str(lcs_count - 1)
                elif lcs_count - 1 > 9:
                    mod = '0' + str(lcs_count - 1)
                elif lcs_count - 1 > 0:
                    mod = '00' + str(lcs_count - 1)

                x = -self.attributes_dict['base_width'] / 2.0 + \
                    across_pos * self.floor_board_kind.width + \
                    self.floor_board_kind.width / 2.0
                y = -self.attributes_dict['base_depth'] / 2.0 + \
                    down_pos * self.floor_board_kind.depth + \
                    self.floor_board_kind.depth / 2.0
                z = self.girder_board_kind.width / 2.0 + \
                    self.joist_board_kind.width

                new_panel = copy.deepcopy(self.floor_board_kind)

                new_panel.b_name = self.floor_board_kind.b_name + '_' + \
                                   str(down_pos + across_pos * self.panels_down)
                new_panel.p_plane = 'XY_Plane' + mod

                for instr in new_panel.generate_for_freecad():
                    instructions_list.append(instr)

                lcs_place = 'App.Placement(App.Vector(' + \
                            str(x) + ',' + str(y) + ',' + str(z) + '),App.Rotation(App.Vector(0,0,1),0))'

                lcs_pos = FC_Ops.freecad_set_document_field_dict(
                    obj='Floor_Board_' + str(down_pos + across_pos * self.panels_down),
                    att='Placement',
                    value=lcs_place
                )

                # instructions_list.append(new_lcs)
                instructions_list.append(lcs_pos)

                lcs_count = lcs_count + 1

        # add the header joist

        for cap_pos in range(0, 2):
            mod = ''

            if lcs_count - 1 > 99:
                mod = str(lcs_count - 1)
            elif lcs_count - 1 > 9:
                mod = '0' + str(lcs_count - 1)
            elif lcs_count - 1 > 0:
                mod = '00' + str(lcs_count - 1)

            new_head_joist = copy.deepcopy(self.header_joist_board_kind)
            new_head_joist.b_name = self.header_joist_board_kind.b_name + '_' + str(cap_pos)
            new_head_joist.p_plane = 'XZ_Plane' + mod

            x = -self.attributes_dict['base_width'] / 2.0 + \
                self.girder_board_kind.thickness / 2.0 + \
                cap_pos * (self.attributes_dict['base_width'] -
                           self.girder_board_kind.thickness)
            y = self.attributes_dict['base_depth'] / 2.0
            z = self.girder_board_kind.width / 2.0 + \
                self.joist_board_kind.width / 2.0

            for instr in new_head_joist.generate_for_freecad():
                instructions_list.append(instr)

            lcs_place = 'App.Placement(App.Vector(' + \
                        str(x) + ',' + str(y) + ',' + str(z) + '),App.Rotation(App.Vector(0,0,1),0))'

            lcs_pos = FC_Ops.freecad_set_document_field_dict(
                obj='Header_Joist_' + str(cap_pos),
                att='Placement',
                value=lcs_place
            )

            instructions_list.append(lcs_pos)

            lcs_count = lcs_count + 1

        self.final_indx = lcs_count

        part_name = 'Floor Frame'

        destination_folder = ''
        fname = part_name + '.FCStd'

        instructions_list.append(
            FC_Ops.freecad_save_file(file_name=part_name, directory=destination_folder)
        )

        return instructions_list