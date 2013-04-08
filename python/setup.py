from __future__ import division
import random
import units as units_module
import settings


class Tiles_bag(object):
    def __init__(self):
        self.tiles = [(column, row) for column in board_columns for row in board_rows]
        
    def pick_from_row(self, rows):
        pick = random.choice([tile for tile in self.tiles if tile[1] in rows])
        self.tiles.remove(pick)
        return pick
   
        
class Unit_bag(object):
    def __init__(self, units):
        self.units = units
    
    def pick(self):
        pick = random.choice(self.units)
        self.units.remove(pick)
        return pick
    
    def has_units(self):
        return self.units

    def remove_units(self, name_list):
        self.units = [unit for unit in self.units if unit not in name_list]

    def remove_one_unit(self, name):
        self.units.remove(name)


board_rows = [1, 2, 3, 4]
board_columns = [1, 2, 3, 4, 5]

siege_weapons = ["Ballista", "Catapult", "Cannon"]



def test_coloumn_blocks(units):
    """ Tests whether there on each coloumn are at least two 'blocks'.
    A block is either a unit, or a Pikeman zoc tile. """
    
    columns = [position[0] + x for x in [-1, +1] for position, unit in units.items() if unit.name == "Pikeman"]\
        + [position[0] for position in units]

    return not any(columns.count(column) < 2 for column in board_columns)
     

def test_pikeman_coloumn(units):
    """ Tests whether there is more than one Pikeman on any coloumn."""
    
    columns = [position[0] for position, unit in units.items() if unit.name == "Pikeman"]
    
    return not any(columns.count(column) > 1 for column in board_columns)


def enforce_max_siege_weapons(units, unit_bag):

    siege_count = sum(1 for unit in units.values() if unit.name in siege_weapons)

    if siege_count >= 2:
        unit_bag.remove_units(siege_weapons)


def get_units():
    
    def select_basic_units(basic_units_bag, tiles_bag):

        units = {}

        if settings.at_least_one_siege_weapon:
            name = random.choice(["Ballista", "Catapult"])
            position = tiles_bag.pick(settings.basic_units[name][0])
            units[position] = getattr(units_module, name.replace(" ", "_"))()
            basic_units_bag.remove_one_unit("Ballista")
            basic_units_bag.remove_one_unit("Catapult")


        while len(units) < settings.basic_unit_count:

            if settings.max_two_siege_weapons:
                enforce_max_siege_weapons(units, basic_units_bag)

            name = basic_units_bag.pick()
            position = tiles_bag.pick(settings.basic_units[name][0])

            units[position] = getattr(units_module, name.replace(" ", "_"))()

        unitlist = [unit for unit in units.values()]

        random.shuffle(unitlist)

        unitlist[0].attack_counters = 1
        unitlist[1].defence_counters = 1

        return units

    def select_special_units(special_units_first_bag, special_units_second_bag, tiles_bag, units):

        total_unit_count = settings.basic_unit_count + settings.special_unit_count

        while len(units) < total_unit_count and special_units_first_bag.has_units():

            if settings.max_two_siege_weapons:
                enforce_max_siege_weapons(units, special_units_first_bag)

            name = special_units_first_bag.pick()
            position = tiles_bag.pick(settings.special_units[name])
            units[position] = getattr(units_module, name.replace(" ", "_"))()

        while len(units) < total_unit_count:

            if settings.max_two_siege_weapons:
                enforce_max_siege_weapons(units, special_units_second_bag)

            name = special_units_second_bag.pick()
            position = tiles_bag.pick(settings.special_units[name])
            units[position] = getattr(units_module, name.replace(" ", "_"))()

        return units

    def fill_bags():
        
        basic_units_bag = Unit_bag([name for name in settings.basic_units for _ in range(settings.basic_units[name][1])])
        
        special_units_first_bag = Unit_bag(list(settings.use_special_units))
        
        special_units_second_bag = Unit_bag(list(set(settings.special_units) - set(settings.dont_use_special_units)
                                                 - set(settings.use_special_units)))

        tiles_bag = Tiles_bag()
        
        return basic_units_bag, special_units_first_bag, special_units_second_bag, tiles_bag
        
    while True:
        
        basic_units_bag, special_units_first_bag, special_units_second_bag, tiles_bag = fill_bags()
        
        try:
            units = select_basic_units(basic_units_bag, tiles_bag)
            units = select_special_units(special_units_first_bag, special_units_second_bag, tiles_bag, units)
        except IndexError:
            continue

        if any(not requirement(units) for requirement in [test_coloumn_blocks, test_pikeman_coloumn]):
            continue
             
        return units


def flip_units(units):
    
    def flip(position):
        return position[0], 9 - position[1]
    
    return dict((flip(position), unit) for position, unit in units.items())


def get_start_units():

    player1_units = get_units()
    player2_units = flip_units(get_units())
    
    return player1_units, player2_units
