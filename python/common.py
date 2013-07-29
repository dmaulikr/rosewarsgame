from json import JSONEncoder, dumps
from datetime import datetime
from bson import ObjectId
from collections import namedtuple


class Direction:
    """ An object direction is one move up, down, left or right.
    The class contains methods for returning the tile going one step in the direction will lead you to,
    and for returning the tiles you should check for zone of control.
    """

    to_coordinates = {"Left": (-1, 0), "Right": (1, 0), "Down": (0, -1), "Up": (0, 1),
                      "Up-Left": (-1, 1), "Up-Right": (1, 1), "Down-Left": (-1, -1), "Down-Right": (-1, 1)}

    def __init__(self, name):
        self.x, self.y = self.to_coordinates[name]
        self.name = name

    def move(self, position):
        return Position(position.column + self.x, position.row + self.y)

    def perpendicular(self, position):
        return Position(position.column + self.y, position.row + self.x), \
            Position(position.column - self.y, position.row - self.x)

    def __repr__(self):
        return self.name


board_height = 8
board_width = 5
board = set((column, row) for column in range(1, board_width + 1) for row in range(1, board_height + 1))
directions = {Direction(name) for name in ["Up", "Down", "Left", "Right"]}
eight_directions = {Direction(name) for name in Direction.to_coordinates}


def position_to_string(position):
    if position:
        return " ABCDE"[position.column] + str(position.row)

Position = namedtuple("Position", ["column", "row"])
Position.__repr__ = position_to_string


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

SubOutcome = enum("UNKNOWN", "WIN", "PUSH", "MISS", "DEFEND", "DETERMINISTIC")
MoveOrStay = enum("UNKNOWN", "MOVE", "STAY")


def position_to_tuple(position_string):
    if position_string and len(position_string) == 2:
        return Position(ord(position_string[0]) - 64, int(position_string[1]))  # In ASCII A, B,.. is 65, 66, ..


def merge_units(units1, units2):
    all_units = units1.copy()
    all_units.update(units2)
    return all_units


def distance(position1, position2):
    return abs(position1.column - position2.column) + abs(position1.row - position2.row)


def get_direction(position, forward_position):
    """ Returns the direction that would take you from position to forward_position """
    return next(direction for direction in directions if direction.move(position) == forward_position)


def flip(position):
    return Position(position.column, board_height - position.row + 1)


def four_forward_tiles(position, forward_position):
    """ Returns the 4 other nearby tiles in the direction towards forward_position """
    return surrounding_tiles(position) & surrounding_tiles(forward_position)


def adjacent_tiles(position):
    """Returns the 4 tiles that is one move away from position"""
    return set(direction.move(position) for direction in directions)


def two_forward_tiles(position, forward_position):
    """ Returns the 2 other nearby tiles in the direction towards forward_position """
    return adjacent_tiles(forward_position) & surrounding_tiles(position)


def surrounding_tiles(position):
    """ Returns the 8 surrounding tiles"""
    return set(direction.move(position) for direction in eight_directions)


def out_of_board_vertical(position):
    return position.row < 1 or position.row > board_height


def out_of_board_horizontal(position):
    return position.column < 1 or position.column > board_width


def find_all_friendly_units_except_current(current_unit_position, player_units):
    return dict((position, player_units[position]) for position in player_units if position != current_unit_position)


class CustomJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj.strftime("%Y-%m-%dT%H:%M:%SZ"))
        if isinstance(obj, ObjectId):
            return str(obj)
        return JSONEncoder.default(self, obj)


def document_to_string(document):
    return dumps(document, indent=4, cls=CustomJsonEncoder)



