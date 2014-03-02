import json
from gamestate import Gamestate
from action import Action
import action_getter
import battle
from outcome import Outcome
import glob
from unittest import TestCase, TextTestRunner, TestSuite
from common import assert_equal_documents, enum_attributes
import sys
from tests.replaytestcase import ReplayTestCase


class UniversalTestCase(TestCase):
    def __init__(self, testcase_file):
        super(UniversalTestCase, self).__init__()
        self.testcase_file = testcase_file
        self.description = None

    def runTest(self):
        try:
            test_document = json.loads(open(self.testcase_file).read())

            if "description" in test_document:
                self.description = test_document["description"]

            if test_document["type"] == "Does action exist":
                gamestate = Gamestate.from_document(test_document["gamestate"])
                action = Action.from_document(gamestate.all_units(), test_document["action"])
                expected = test_document["result"]
                self.does_action_exist(gamestate, action, expected)

            elif test_document["type"] == "Is attack and defence correct":
                gamestate = Gamestate.from_document(test_document["gamestate"])
                action = Action.from_document(gamestate.all_units(), test_document["action"])
                attack = test_document["attack"]
                defence = test_document["defence"]

                self.is_attack_and_defence_correct(gamestate, action, attack, defence)

            elif test_document["type"] == "Is outcome correct":
                gamestate = Gamestate.from_document(test_document["pre_gamestate"])
                expected_gamestate = Gamestate.from_document(test_document["post_gamestate"])
                action = Action.from_document(gamestate.all_units(), test_document["action"])
                outcome = None
                if "outcome" in test_document:
                    outcome = Outcome.from_document(test_document["outcome"])

                if action.move_with_attack:
                    # If move-with-attack is set, test both the situation where it
                    # is registered right away, and the situation where it is registered
                    # in a two-step process
                    gamestate_delayed = gamestate.copy()
                    action_delayed = Action.from_document(gamestate_delayed.all_units(), test_document["action"])
                    action_delayed.move_with_attack = None
                    self.is_outcome_correct(gamestate_delayed, action_delayed, outcome, expected_gamestate)

                self.is_outcome_correct(gamestate, action, outcome, expected_gamestate)

            elif test_document["type"] == "Does turn shift work":
                gamestate = Gamestate.from_document(test_document["pre_gamestate"])
                expected_gamestate = Gamestate.from_document(test_document["post_gamestate"])

                self.is_turn_shift_correct(gamestate, expected_gamestate)

            elif test_document["type"] == "Upgrade":
                gamestate = Gamestate.from_document(test_document["pre_gamestate"])
                expected_gamestate = Gamestate.from_document(test_document["post_gamestate"])

                if isinstance(test_document["upgrade"], basestring):
                    upgrade_choice = test_document["upgrade"]
                else:
                    upgrade_choice = enum_attributes(test_document["upgrade"])

                self.upgrade(gamestate, upgrade_choice, expected_gamestate)

            elif test_document["type"] == "Is outcome correct, extra action":
                return

            else:
                self.assertTrue(False, "Unknown test type: " + test_document["type"])

        except ValueError as error:
            self.assertTrue(False, "Failed to load test document: " + self.testcase_file + "\n\n" + error.message)

    def is_turn_shift_correct(self, gamestate, expected_gamestate):

        gamestate.shift_turn()
        gamestate.flip_all_units()

        actual_gamestate_document = gamestate.to_document()
        expected_gamestate_document = expected_gamestate.to_document()

        assert_equal_documents(self, expected_gamestate_document, actual_gamestate_document, self.testcase_file)

    def does_action_exist(self, gamestate, action, expected):
        available_actions = action_getter.get_actions(gamestate)
        actual = (action in available_actions)

        message = "Wrong action existance for " + self.testcase_file + "\n\n"
        if self.description:
            message += "Description: " + self.description + "\n\n"
        if expected:
            message += "Requested action: " + str(action) + "\n"
        else:
            message += "Not-allowed action: " + str(action) + "\n"

        message += "Available actions:\n"
        for available_action in available_actions:
            message += str(available_action) + "\n"

        self.assertEqual(actual, expected, message)

    def is_attack_and_defence_correct(self, gamestate, action, expected_attack, expected_defence):
        actual_attack = action.get_attack(gamestate)
        actual_defence = action.get_defence(gamestate)

        error_string = "Filename" + self.testcase_file + "\n" + \
                       "Expected attack / defence " + str(expected_attack) + "," + str(expected_defence) + "\n" + \
                       "Actual attack / defence " + str(actual_attack) + "," + str(actual_defence) + "\n" \


        self.assertEqual(actual_attack, expected_attack, error_string)
        self.assertEqual(actual_defence, expected_defence, error_string)

    def is_outcome_correct(self, gamestate, action, outcome, expected_gamestate):
        gamestate.do_action(action, outcome)

        if action.move_with_attack is None:
            action.move_with_attack = True
            gamestate.move_melee_unit_to_target_tile(outcome.for_position(action.target_at), action)

        actual_gamestate_document = gamestate.to_document()
        expected_gamestate_document = expected_gamestate.to_document()

        assert_equal_documents(self, expected_gamestate_document, actual_gamestate_document, self.testcase_file)

    def upgrade(self, gamestate, upgrade_choice, expected_gamestate):
        for position, unit in gamestate.player_units.items():
            if unit.is_allowed_upgrade_choice(upgrade_choice):
                gamestate.player_units[position] = unit.get_upgraded_unit(upgrade_choice)

        assert_equal_documents(self, expected_gamestate.to_document(), gamestate.to_document(), self.testcase_file)


if __name__ == "__main__":
    runner = TextTestRunner()

    suite = TestSuite()

    testcase_files = list()
    replay_files = list()
    if len(sys.argv) == 2:
        if "replay" in sys.argv[1]:
            replay_files.append(sys.argv[1])
        else:
            testcase_files.append(sys.argv[1])
    else:
        testcase_files = glob.glob("./../sharedtests_1.1/*/*.json")
        #replay_files = glob.glob("replay/*/*.json")
        #testcase_files = ["./../sharedtests_1.1/Flanking_Cavalry/AD_Flanking_3.json"]

    for testcase_file in testcase_files:
        suite.addTest(UniversalTestCase(testcase_file))

    for replay_file in replay_files:
        suite.addTest(ReplayTestCase(replay_file))

    runner.run(suite)
