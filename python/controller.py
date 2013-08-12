from __future__ import division
import pygame
import sys
from pygame.locals import *
import setup
from gamestate import Gamestate
import os
import settings
from player import Player
from action import Action
import units as units_module
from client import Client
from game import Game
from outcome import Outcome
import json
from common import *


class Controller(object):
    def __init__(self, view):
        self.view = view
        self.game = None
        self.client = None

    @classmethod
    def new_game(cls, view):
        if not os.path.exists("./replay"):
            os.makedirs("./replay")

        controller = Controller(view)

        players = [Player("Green", settings.player1_ai), Player("Red", settings.player2_ai)]

        player1_units, player2_units = setup.get_start_units()
        gamestate = Gamestate(player1_units, player2_units, 1)

        controller.game = Game(players, gamestate)

        controller.game.gamestate.initialize_turn()

        controller.game.gamestate.actions_remaining = 1

        controller.clear_move()

        return controller

    @classmethod
    def from_network(cls, view, game_id, player):
        controller = cls(view)

        controller.game_id = game_id
        controller.client = Client(game_id)

        controller.gamestate = controller.client.get_gamestate()
        controller.gamestate.set_network_player(player)

        controller.clear_move()

        return controller

    @classmethod
    def from_replay(cls, view, savegame_file):
        controller = cls(view)
        savegame_document = json.loads(open(savegame_file).read())
        controller.gamestate = Gamestate.from_log_document(savegame_document)
        players = [Player("Green", settings.player1_ai), Player("Red", settings.player2_ai)]
        controller.game = Game(players, controller.gamestate)
        controller.clear_move()

        return controller

    def trigger_network_player(self):
        action, outcome = self.client.select_action(self.game.gamestate.action_number)

        print "received action from network: " + str(action)

        self.perform_action(action, outcome)

        if hasattr(self.game.gamestate.current_player(), "extra_action"):
            extra_action, extra_outcome = self.client.select_action(self.game.gamestate)
            self.perform_action(extra_action, extra_outcome)

    def trigger_artificial_intelligence(self):

        action = self.game.current_player().ai.select_action(self.game)

        if action:
            self.perform_action(action)
        else:
            self.game.shift_turn()
            self.view.draw_game(self.game)

        if getattr(self.game.gamestate, "extra_action"):
            extra_action = self.game.current_player().ai.select_action(self.game.gamestate)
            self.perform_action(extra_action)

    def left_click(self, position):

        if self.selecting_ability_target(position):
            if len(self.selected_unit.abilities) > 1:
                index = self.get_input_abilities(self.selected_unit)

                ability = self.selected_unit.abilities[index]
            else:
                ability = self.selected_unit.abilities[0]

            action = Action(self.game.gamestate.all_units(), self.start_at, target_at=position, ability=ability)
            if action in self.game.gamestate.get_actions():
                self.perform_action(action)
            else:
                self.clear_move()
                self.view.draw_game(self.game)

        elif self.selecting_active_unit(position):
            self.start_at = position
            self.selected_unit = self.game.gamestate.player_units[self.start_at]
            illustrate_actions = [action for action in self.game.gamestate.get_actions() if action.start_at == position]
            self.view.draw_game(self.game, position, illustrate_actions)

        elif self.selecting_ranged_target(position):
            action = Action(self.game.gamestate.all_units(), self.start_at, target_at=position)
            if action in self.game.gamestate.get_actions():
                self.perform_action(action)

        elif self.selecting_melee_target(position):
            all_actions = self.game.gamestate.get_actions()

            possible_actions = [action for action in all_actions if self.possible_melee_target(action, position)]

            if not possible_actions:
                return

            if len(possible_actions) == 1:
                action = possible_actions[0]
            else:
                self.view.draw_game(self.game)
                action = self.pick_action_end_position(possible_actions)

            # Human actions always start out with unknown move_with_attack (they are asked later)
            action.move_with_attack = None

            self.perform_action(action)

        elif self.selecting_move(position):
            action = Action(self.game.gamestate.all_units(), self.start_at, end_at=position)
            if action in self.game.gamestate.get_actions():
                self.perform_action(action)
            else:
                self.clear_move()
                self.view.draw_game(self.game)

        elif self.start_at and self.start_at == position:
            self.clear_move()
            self.view.draw_game(self.game)

    def possible_melee_target(self, action, position):
        same_start = action.start_at == self.start_at
        same_target = action.target_at and action.target_at == position
        return same_start and same_target and not action.move_with_attack

    def pick_action_end_position(self, possible_actions):

        end_positions = [action.end_at for action in possible_actions]

        self.view.shade_positions(end_positions)

        while True:
            event = pygame.event.wait()

            if event.type == pygame.MOUSEBUTTONDOWN:
                position = self.view.get_position_from_mouse_click(event.pos)

                if event.button == 1:
                    for action in possible_actions:
                        if position == action.end_at:
                            return action

            elif self.quit_game_requested(event):
                self.exit_game()

    def right_click(self, position):
        if not self.start_at:
            self.show_unit(position)
        else:
            if position in self.game.gamestate.enemy_units:
                self.show_attack(position)

    def clear_move(self):
        self.start_at = self.end_position = self.selected_unit = None

    def run_game(self):

        self.game.gamestate.set_available_actions()

        self.view.draw_game(self.game)

        while True:
            event = pygame.event.wait()

            if event.type == pygame.MOUSEBUTTONDOWN:
                position = self.view.get_position_from_mouse_click(event.pos)

                if event.button == 1:
                    self.left_click(position)
                elif event.button == 3:
                    self.right_click(position)

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.clear_move()
                self.view.draw_game(self.game)

            elif self.quit_game_requested(event):
                self.exit_game()

            self.view.refresh()

    def exit_game(self):
        sys.exit()

    def get_input_upgrade(self, unit):
        self.view.draw_upgrade_options(unit)

        while True:
            event = pygame.event.wait()

            if event.type == KEYDOWN and event.key == K_1:
                return 0

            if event.type == KEYDOWN and event.key == K_2:
                return 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if within(event.pos, self.view.interface.upgrade_1_area):
                        return 0
                    elif within(event.pos, self.view.interface.upgrade_2_area):
                        return 1

            elif self.quit_game_requested(event):
                self.exit_game()

    def get_input_abilities(self, unit):
        self.view.draw_ask_about_ability(unit)

        while True:
            event = pygame.event.wait()

            if event.type == KEYDOWN and event.key == K_1:
                return 0

            if event.type == KEYDOWN and event.key == K_2:
                return 1

            elif self.quit_game_requested(event):
                self.exit_game()

    def ask_about_move_with_attack(self, action):

        self.view.draw_ask_about_move_with_attack(action.target_at)

        while True:
            event = pygame.event.wait()

            if event.type == pygame.MOUSEBUTTONDOWN:
                position = self.view.get_position_from_mouse_click(event.pos)

                if event.button == 1:
                    if position == action.target_at:
                        return True
                    if position == action.end_at:
                        return False

            elif self.quit_game_requested(event):
                self.exit_game()

    def pause(self):
        while True:
            event = pygame.event.wait()

            if self.quit_game_requested(event):
                self.exit_game()

            elif event.type == KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

    def upgrade_unit(self, position, unit):
        if unit.get(Trait.xp) < unit.xp_to_upgrade:
            return

        choice = self.get_input_upgrade(unit)

        if isinstance(unit.upgrades[0], str):
            upgrade_choice = unit.upgrades[choice]
            upgrade = getattr(units_module, upgrade_choice.replace(" ", "_"))()
        else:
            upgrade = getattr(units_module, unit.name.replace(" ", "_"))()
            upgrade.constants = unit.constants.copy()
            for upgrade_trait, value in unit.upgrades[0][choice].items():
                upgrade.constants[upgrade_trait] = value
            if Trait.level in upgrade.constants:
                upgrade.constants[Trait.level] += 1
            else:
                upgrade.constants[Trait.level] = 2

        self.game.gamestate.player_units[position] = upgrade

    def perform_action(self, action, outcome=None):

        self.draw_action = True

        self.view.draw_game(self.game)

        if self.game.current_player().intelligence == "Human":

            if self.game.opponent_player().intelligence == "Network":
                outcome = self.client.send_action(action.to_document())
                action.ensure_outcome(outcome)

            outcome = Outcome.determine_outcome(action, self.game.gamestate)

            self.game.do_action(action, outcome)

            self.view.draw_game(self.game)
            self.view.draw_action(action, outcome, self.game)

            if self.is_post_movement_possible(action, outcome):
                move_with_attack = self.ask_about_move_with_attack(action)

                self.game.save_option("move_with_attack", move_with_attack)

                if move_with_attack:
                    self.game.gamestate.move_melee_unit_to_target_tile(action)

        else:
            if not outcome:
                outcome = Outcome.determine_outcome(action, self.game.gamestate)

            self.game.do_action(action, outcome)
            self.view.draw_action(action, outcome, self.game, flip=True)

        if action.move_with_attack:
            self.view.draw_post_movement(action, self.game)

        self.game.save(self.view, action, outcome)

        if action.is_attack():
            if settings.pause_for_attack_until_click:
                self.pause()
            else:
                pygame.time.delay(settings.pause_for_animation_attack)
        else:
            pygame.time.delay(settings.pause_for_animation)

        if self.game.gamestate.is_ended():
            self.game_end(self.game.current_player())
            return

        if self.game.current_player().intelligence == "Human":
            self.view.draw_game(self.game)
            if action.target_at in self.game.gamestate.player_units:
                self.upgrade_unit(action.target_at, action.unit)
            else:
                self.upgrade_unit(action.end_at, action.unit)

        self.view.draw_game(self.game)

        if self.game.gamestate.is_turn_done():
            self.game.shift_turn()

        self.view.draw_game(self.game)

        self.clear_move()

        if self.game.current_player().intelligence not in ["Human", "Network"]:
            self.trigger_artificial_intelligence()
        elif self.game.current_player().intelligence == "Network":
            self.trigger_network_player()

    def is_post_movement_possible(self, action, outcome):
        if not action.is_attack():
            return False

        if not action.move_with_attack is None and not action.move_with_attack:
            return False

        is_successful = action.is_successful(outcome.for_position(action.target_at), self.game.gamestate)
        is_destination_occupied = action.target_at in self.game.gamestate.enemy_units

        return is_successful and action.unit.is_melee() and not is_destination_occupied

    def show_attack(self, attack_position):
        action = Action(self.game.gamestate.all_units(), self.start_at, target_at=attack_position)
        player_unit = self.game.gamestate.player_units[self.start_at]

        opponent_unit = self.game.gamestate.enemy_units[attack_position]
        self.view.show_attack(self.game.gamestate, action, player_unit, opponent_unit)

        return

    def show_unit(self, position):

        unit = None
        if position in self.game.gamestate.player_units:
            unit = self.game.gamestate.player_units[position]
        if position in self.game.gamestate.enemy_units:
            unit = self.game.gamestate.enemy_units[position]

        if unit:
            self.view.show_unit_zoomed(unit)
            self.pause()
            self.view.draw_game(self.game)
            return

    def quit_game_requested(self, event):
        return event.type == QUIT or (event.type == KEYDOWN and self.command_q_down(event.key))

    def command_q_down(self, key):
        return key == K_q and (pygame.key.get_mods() & KMOD_LMETA or pygame.key.get_mods() & KMOD_RMETA)

    def game_end(self, player):
        self.view.draw_game_end(player.color)
        self.pause()
        self.exit_game()

    def selecting_active_unit(self, position):
        selecting_player_unit = position in self.game.gamestate.player_units
        if self.start_at is None:
            return selecting_player_unit
        else:
            return self.start_at != position and selecting_player_unit

    def selecting_ability_target(self, position):
        if not self.start_at:
            return False

        return position in self.game.gamestate.all_units() and self.selected_unit.abilities

    def selecting_ranged_target(self, position):
        if not self.start_at:
            return False

        return position in self.game.gamestate.enemy_units and self.selected_unit.is_ranged()

    def selecting_melee_target(self, position):
        if not self.start_at:
            return False

        return position in self.game.gamestate.enemy_units and self.selected_unit.is_melee()

    def selecting_move(self, position):
        return self.start_at and position not in self.game.gamestate.all_units()


def within(point, area):
    return area[0].y <= point[1] <= area[1].y and area[0].x <= point[0] <= area[1].x
