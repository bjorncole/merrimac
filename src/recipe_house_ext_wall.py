import compound_cameo as MD_Cmp

import compound_freecad as FC_Cmp
import core_freecad_ops as FC_Ops

import recipe_house_floor as RHF

import math
import copy

class T_Housing_Hole():

    '''
    A class to hold the general shape of a hole around which to
    build the wall frame
    '''

    def __init__(self):
        self.width = 0.0
        self.height = 0.0
        self.height_from_floor = 0.0
        self.position = 0.0


class T_Housing_Wall_Frame(MD_Cmp.T_Sysml_Block, FC_Cmp.T_Geom_Assembly):
    def __init__(self, order):
        super().__init__(order)
        self._holes = []
        self.boards_across = 0
        self.direction = ''
        self.push_x = 0.0
        self.push_y = 0.0
        self.push_z = 0.0
        self.push_indx = 1
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
    def base_length(self):
        try:
            return self.attributes_dict['base_length']
        except:
            return ''

    @base_length.setter
    def base_length(self, value):
        val_base = value / 16.0
        val_flush = round(val_base, 0) * 16.0
        self.boards_across = math.floor(val_flush / 16.0) + 1
        self.attributes_dict.update({'base_length': val_flush})
        self.att_types_dict.update({'base_length': 'Real'})

    @property
    def base_height(self):
        try:
            return self.attributes_dict['base_height']
        except:
            return ''

    @base_height.setter
    def base_height(self, value):
        self.attributes_dict.update({'base_height': value})
        self.att_types_dict.update({'base_height': 'Real'})

    @property
    def sill_board_kind(self):
        try:
            return self.part_types_dict['Sill']
        except:
            return ''

    @sill_board_kind.setter
    def sill_board_kind(self, board_obj):
        self.part_types_dict.update({'Sill': board_obj})

    @property
    def plate_board_kind(self):
        try:
            return self.part_types_dict['Plate']
        except:
            return ''

    @plate_board_kind.setter
    def plate_board_kind(self, board_obj):
        self.part_types_dict.update({'Plate': board_obj})

    @property
    def stud_board_kind(self):
        try:
            return self.part_types_dict['Stud']
        except:
            return ''

    @stud_board_kind.setter
    def stud_board_kind(self, board_obj):
        self.part_types_dict.update({'Stud': board_obj})

    @property
    def lintel_board_kind(self):
        try:
            return self.part_types_dict['Lintel']
        except:
            return ''

    @lintel_board_kind.setter
    def lintel_board_kind(self, board_obj):
        self.part_types_dict.update({'Lintel': board_obj})

    @property
    def nogging_kind(self):
        try:
            return self.part_types_dict['Nogging']
        except:
            return ''

    @nogging_kind.setter
    def nogging_kind(self, board_obj):
        self.part_types_dict.update({'Nogging': board_obj})

    @property
    def holes(self):
        return self._holes

    @holes.setter
    def holes(self, hole_list):
        self._holes = copy.deepcopy(hole_list)

    def generate_for_freecad(self):
        # instructions_list = super().generate_for_freecad()

        instructions_list = []

        # make attach point local coordinate systems - one at +1/2Y and one at -1/2X

        lcs_count = self.push_indx

        # set up plates

        plate_plane = ''

        if self.direction == 'North-South':
            plate_plane = 'XZ_Plane'
        elif self.direction == 'East-West':
            plate_plane = 'YZ_Plane'

        stud_count = 0
        jack_stud_count = 0

        stud_prefix = ''

        for plate_pos in range(0, 2):
            mod = ''
            if lcs_count - 1 > 99:
                mod = str(lcs_count - 1)
            elif lcs_count - 1 > 9:
                mod = '0' + str(lcs_count - 1)
            elif lcs_count - 1 > 0:
                mod = '00' + str(lcs_count - 1)

            new_plate = copy.deepcopy(self.plate_board_kind)
            new_plate.b_name = self.plate_board_kind.b_name + '_' + str(plate_pos)
            new_plate.p_plane = plate_plane + mod

            for instr in new_plate.generate_for_freecad():
                instructions_list.append(instr)

            x = 0.0
            y = 0.0

            if self.direction == 'North-South':
                y = self.attributes_dict['base_length'] / 2.0
            elif self.direction == 'East-West':
                x = -self.attributes_dict['base_length'] / 2.0

            z = (self.stud_board_kind.width + self.stud_board_kind.length) * plate_pos

            lcs_place = 'App.Placement(App.Vector(' + \
                        str(x + self.push_x) + ',' + str(y + self.push_y) + \
                        ',' + str(z + self.push_z) + \
                        '),App.Rotation(App.Vector(0,0,1),0))'

            lcs_pos = FC_Ops.freecad_set_document_field_dict(
                obj=self.plate_board_kind.b_name + '_' + str(plate_pos),
                att='Placement',
                value=lcs_place
            )
            # instructions_list.append(new_lcs)
            instructions_list.append(lcs_pos)

            lcs_count = lcs_count + 1

        for stud_pos in range(0, self.boards_across):

            mod = ''
            if lcs_count - 1 > 99:
                mod = str(lcs_count - 1)
            elif lcs_count - 1 > 9:
                mod = '0' + str(lcs_count - 1)
            elif lcs_count - 1 > 0:
                mod = '00' + str(lcs_count - 1)

            # TODO: Cut down studs where there is a hole

            lower_stud_length = 0.0
            upper_stud_length = 0.0
            upper_stud_z = 0.0

            stud_cut = False
            number_boards = 1

            z = self.stud_board_kind.width / 2.0

            for hole in self.holes:
                stud_center = stud_pos * 16.0

                # stud center inside hole means it is cut
                hole_min = hole.position
                hole_max = hole.position + hole.width

                if stud_center >= hole_min and stud_center <= hole_max:
                    stud_cut = True
                    upper_stud_z = hole.height_from_floor + hole.height + \
                                   self.stud_board_kind.width / 2.0

                    lower_stud_length = hole.height_from_floor
                    upper_stud_length = self.stud_board_kind.length - upper_stud_z

                    if hole.height_from_floor > 0.0:
                        number_boards = 2
                else:
                    pass

            for local_pos in range(0, number_boards):

                the_count = 0

                if not stud_cut:
                    stud_count = stud_count + 1
                    the_count = stud_count
                    stud_prefix = ''

                stud_length = 0.0

                new_stud = copy.deepcopy(self.stud_board_kind)

                if stud_cut:
                    # start from top down
                    jack_stud_count = jack_stud_count + 1
                    the_count = jack_stud_count
                    stud_prefix = 'Jack_'
                    if local_pos == 0:
                        z = upper_stud_z
                        new_stud.length = upper_stud_length
                    else:
                        new_stud.length = lower_stud_length
                        z = self.stud_board_kind.width / 2.0

                new_stud.b_name = stud_prefix + self.stud_board_kind.b_name + '_' + str(the_count)
                new_stud.p_plane = 'XY_Plane' + mod

                for instr in new_stud.generate_for_freecad():
                    instructions_list.append(instr)

                y_cheat = 0.0

                if stud_pos == self.boards_across - 1:
                    loc_cheat = -self.stud_board_kind.width / 2.0

                if stud_pos == 0:
                    loc_cheat = self.stud_board_kind.width / 2.0

                x = 0.0
                y = 0.0

                if self.direction == 'North-South':
                    y = self.attributes_dict['base_length'] / 2.0 - 16.0 * stud_pos - loc_cheat
                elif self.direction == 'East-West':
                    x = -self.attributes_dict['base_length'] / 2.0 + 16.0 * stud_pos + loc_cheat

                lcs_place = 'App.Placement(App.Vector(' + \
                            str(x + self.push_x) + ',' + str(y + self.push_y) + \
                            ',' + str(z + self.push_z) + \
                            '),App.Rotation(App.Vector(0,0,1),0))'

                lcs_pos = FC_Ops.freecad_set_document_field_dict(
                    obj=stud_prefix + 'Stud_' + str(the_count),
                    att='Placement',
                    value=lcs_place
                )

                # instructions_list.append(new_lcs)
                instructions_list.append(lcs_pos)

                lcs_count = lcs_count + 1

        part_name = 'Wall Frame'

        destination_folder = ''
        fname = part_name + '.FCStd'

        instructions_list.append(
            FC_Ops.freecad_save_file(file_name=part_name, directory=destination_folder)
        )

        return instructions_list