from gamestate.gamestate_library import Effect, State

remove_states = {State.used, State.recently_bribed}
wear_off_in_opponents_turn = {Effect.poisoned}
wear_off_states = {State.attack_frozen}


def return_bribed_units(gamestate):
    for position, unit in list(gamestate.enemy_units.items()):
        if unit.has(Effect.bribed):
            unit.remove(Effect.bribed)
            gamestate.change_unit_owner(position)
            unit.set(State.recently_bribed)


def adjust_states_and_effects(gamestate):

    for position, unit in gamestate.player_units.items():
        for state in remove_states:
            unit.remove(state)
        for state in wear_off_states:
            unit.decrease(state)
        for effect in set(unit.effects) - wear_off_in_opponents_turn:
            unit.decrease(effect)


    for position, unit in gamestate.enemy_units.items():
        for effect in wear_off_in_opponents_turn:
            unit.decrease(effect)
        for state in remove_states:
            unit.remove(state)


def initialize_turn(gamestate):

    gamestate.set_actions_remaining(2)

    adjust_states_and_effects(gamestate)

    return_bribed_units(gamestate)

