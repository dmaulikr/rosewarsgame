from __future__ import division
import pygame
import sys
from pygame.locals import *
import setup
from gamestate_module import Gamestate
import os
import settings
import shutil
from player import Player
from action import Action


class Controller(object):
    def __init__(self, view):
        self.view = view

        self.action_index = 1

        player1 = Player("Green")
        player2 = Player("Red")

        player1.ai_name = settings.player1_ai
        player2.ai_name = settings.player2_ai

        player1_units, player2_units = setup.get_start_units()

        self.gamestate = Gamestate(player1, player1_units, player2, player2_units)

        self.gamestate.initialize_turn()
        self.gamestate.initialize_action()

        self.gamestate.set_actions_remaining(1)

        if os.path.exists("./replay"):
            shutil.rmtree('./replay')

        os.makedirs("./replay")

        self.clear_move()

    def trigger_artificial_intelligence(self):

        action = self.gamestate.current_player().ai.select_action(self.gamestate)

        if action:
            self.perform_action(action)
        else:
            self.gamestate.turn_shift()
            self.gamestate.recalculate_special_counters()
            self.view.draw_game(self.gamestate)

        if hasattr(self.gamestate.current_player(), "extra_action"):
            extra_action = self.gamestate.current_player().ai.select_action(self.gamestate)
            self.perform_action(extra_action)

    def left_click(self, position):
        if self.deselecting_active_unit(position):
            self.clear_move()
            self.view.draw_game(self.gamestate)

        elif self.selecting_active_unit(position):
            self.start_position = position
            self.selected_unit = self.gamestate.player_units()[self.start_position]
            illustrate_actions = (action for action in self.gamestate.get_actions() if action.start_position == position)
            self.view.draw_game(self.gamestate, position, illustrate_actions)

        elif self.selecting_ability_target(position):
            if len(self.selected_unit.abilities) > 1:
                index = self.get_input_abilities(self.selected_unit)

                ability = self.selected_unit.abilities[index]
            else:
                ability = self.selected_unit.abilities[0]

            action = Action(self.start_position, ability_position=position, ability=ability)
            self.perform_action(action)

        elif self.selecting_ranged_target(position):
            action = Action(self.start_position, attack_position=position)
            self.perform_action(action)

        elif self.selecting_melee_target(position):

            possible_actions = [action for action in self.gamestate.get_actions() if
                                action.start_position == self.start_position and action.attack_position == position and
                                not action.move_with_attack]

            if not possible_actions:
                self.view.draw_message("Action not possible")
                self.clear_move()
                self.view.draw_game(self.gamestate)
                return

            if len(possible_actions) == 1:
                action = possible_actions[0]
            else:
                self.view.draw_game(self.gamestate)
                action = self.pick_action_end_position(possible_actions)

            self.perform_action(action)

        elif self.selecting_move(position):
            action = Action(self.start_position, end_position=position)
            self.perform_action(action)

    def pick_action_end_position(self, possible_actions):

        end_positions = [action.end_position for action in possible_actions]

        self.view.shade_positions(end_positions)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    position = self.view.get_position_from_mouse_click(event.pos)

                    if event.button == 1:
                        for action in possible_actions:
                            if position == action.end_position:
                                return action

                elif event.type == QUIT:
                    self.exit_game()



    def right_click(self, position):
        if not self.start_position:
            self.show_unit(position)
        else:
            if position in self.gamestate.opponent_units():
                self.show_attack(position)

    def clear_move(self):
        self.start_position = self.end_position = self.selected_unit = None

    def run_game(self):

        self.gamestate.set_ais()
        self.gamestate.set_available_actions()

        self.gamestate.recalculate_special_counters()
        self.view.draw_game(self.gamestate)

        while True:
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    position = self.view.get_position_from_mouse_click(event.pos)

                    if event.button == 1:
                        self.left_click(position)
                    elif event.button == 3:
                        self.right_click(position)

                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.clear_move()
                    self.view.draw_game(self.gamestate)

                elif event.type == KEYDOWN and self.command_q_down(event.key):
                    self.exit_game()

                elif event.type == QUIT:
                    self.exit_game()

                self.view.refresh()

    def exit_game(self):
        sys.exit()

    def get_input_counter(self, unit):
        self.view.draw_ask_about_counter(unit.name)

        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_a:
                    unit.attack_counters += 1
                    return

                if event.type == KEYDOWN and event.key == K_d:
                    unit.defence_counters += 1
                    return

                elif event.type == QUIT:
                    self.exit_game()

    def get_input_abilities(self, unit):
        self.view.draw_ask_about_ability(unit)

        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_1:
                    return 0

                if event.type == KEYDOWN and event.key == K_2:
                    return 1

                elif event.type == QUIT:
                    self.exit_game()

    def ask_about_move_with_attack(self, action):

        self.view.draw_ask_about_move_with_attack(action.attack_position)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    position = self.view.get_position_from_mouse_click(event.pos)

                    if event.button == 1:
                        if position == action.attack_position:
                            return True
                        if position == action.end_position:
                            return False

                elif event.type == QUIT:
                    self.exit_game()

    def pause(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit_game()
                elif event.type == KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return

    def add_counters(self, units):
        for unit in units.values():
            if unit.xp == 2:
                if unit.defence + unit.defence_counters == 4:
                    unit.attack_counters += 1
                else:
                    self.get_input_counter(unit)

                unit.xp = 0

    def perform_action(self, action):

        self.draw_action = True

        self.view.draw_game(self.gamestate)

        if hasattr(self.gamestate.current_player(), "extra_action"):
            all_actions = self.gamestate.get_actions()
        else:
            all_actions = self.gamestate.get_actions()

        matching_actions = 0
        for possible_action in all_actions:
            if action == possible_action:
                matching_actions += 1
                action = possible_action

        if matching_actions == 0:
            self.clear_move()
            self.view.draw_game(self.gamestate)
            self.view.draw_message("Action not allowed")
            return

        assert matching_actions <= 1

        if self.gamestate.current_player().ai == "Human":
            self.gamestate.do_action(action, self)
        else:
            self.gamestate.do_action(action)

        if self.draw_action:
            self.view.draw_action(action, self.gamestate)
        else:
            self.view.draw_log(action, self.gamestate)

        self.save_game()

        if action.is_attack:
            if settings.pause_for_attack_until_click:
                self.pause()
            else:
                pygame.time.delay(settings.pause_for_animation_attack)
        else:
            pygame.time.delay(settings.pause_for_animation)

        if hasattr(self.gamestate.current_player(), "won"):
            self.game_end(self.gamestate.current_player())
            return

        if self.gamestate.current_player().ai_name == "Human":
            self.add_counters(self.gamestate.units[0])
        else:
            self.gamestate.current_player().ai.add_counters(self.gamestate)

        self.gamestate.recalculate_special_counters()
        self.view.draw_game(self.gamestate)

        self.gamestate.initialize_action()

        if (self.gamestate.get_actions_remaining() < 1 or len(all_actions) == 1) \
                and not hasattr(self.gamestate.current_player(), "extra_action"):
            self.gamestate.turn_shift()

        self.gamestate.recalculate_special_counters()
        self.view.draw_game(self.gamestate)

        self.clear_move()

        if self.gamestate.current_player().ai_name != "Human":
            self.trigger_artificial_intelligence()

    def show_attack(self, attack_position):
        action = Action(self.start_position, attack_position=attack_position)
        player_unit = self.gamestate.player_units()[self.start_position]
        opponent_unit = self.gamestate.opponent_units()[attack_position]
        self.view.show_attack(action, player_unit, opponent_unit)

        return

    def show_unit(self, position):

        unit = None
        if position in self.gamestate.units[0]:
            unit = self.gamestate.units[0][position]
        if position in self.gamestate.units[1]:
            unit = self.gamestate.units[1][position]

        if unit:
            self.view.show_unit_zoomed(unit)
            self.pause()
            self.view.draw_game(self.gamestate)
            return

    def save_game(self):
        name = str(self.action_index) + ". " \
            + self.gamestate.current_player().color \
            + ", " \
            + str(self.gamestate.turn) \
            + "." \
            + str(2 - self.gamestate.get_actions_remaining())
        self.view.save_screenshot(name)

        self.action_index += 1

    def command_q_down(self, key):
        return key == K_q and (pygame.key.get_mods() & KMOD_LMETA or pygame.key.get_mods() & KMOD_RMETA)

    def game_end(self, player):
        self.view.draw_game_end(player.color)
        self.pause()
        self.exit_game()

    def selecting_active_unit(self, position):
        return not self.start_position and position in self.gamestate.player_units()

    def selecting_ability_target(self, position):
        return self.start_position and (position in self.gamestate.opponent_units() or position in self.gamestate.player_units()) and self.selected_unit.abilities

    def selecting_attack_target_unit(self, position):
        pass

    def selecting_attack_ranged_target(self, position):
        return self.start_position and position in self.gamestate.opponent_units() and \
            self.selected_unit.range > 1

    def deselecting_active_unit(self, position):
        return self.start_position and self.start_position == position

    def selecting_ranged_target(self, position):
        return self.start_position and position in self.gamestate.opponent_units() and \
            self.selected_unit.range > 1

    def selecting_melee_target(self, position):
        return self.start_position and position in self.gamestate.opponent_units() and \
            self.selected_unit.range == 1

    def selecting_move(self, position):
        return self.start_position and position not in self.gamestate.opponent_units()