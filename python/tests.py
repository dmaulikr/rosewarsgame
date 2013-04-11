import unittest
import re
from datetime import datetime
import units as units_module
import ai_module
from player import Player
from gamestate_module import Gamestate
from document import DocumentConverter
from pymongo import MongoClient
from bson.objectid import ObjectId
from pprint import PrettyPrinter


class TestAI(unittest.TestCase):
    def test_GamestateDocument_WhenAnActionIsTaken_ItShouldBeReflected(self):
        converter = DocumentConverter()
        gamestate_document = self.get_test_gamestate_document()
        gamestate = Gamestate.from_document(gamestate_document)
        action = converter.document_to_action({"start_position": "D6", "end_position": "D7"})

        gamestate.do_action(action)
        gamestate.shift_turn_if_done()

        actual = converter.gamestate_to_document(gamestate)
        expected = gamestate_document

        player2_units = expected["player2_units"]
        expected["player2_units"] = {"D7": expected["player1_units"]["D6"]}
        expected["player1_units"] = player2_units
        expected["turn"] += 1
        expected["actions_remaining"] = 2

        self.assert_equal_documents(expected, actual)

    def test_GamestateDocument_WhenSavingAndLoadingDocument_ThenItShouldBeTheSame(self):
        document = self.get_test_gamestate_document()
        converter = DocumentConverter()
        gamestate = Gamestate.from_document(document)
        same_document = converter.gamestate_to_document(gamestate)

        self.assert_equal_documents(document, same_document)

    def test_pymongo_WhenAGameIsInTheDatabase_ThenWeShouldBeAbleToFindIt(self):
        client = MongoClient()
        database = client.unnamed
        games = database.games

        game = games.find_one({"_id": ObjectId("51521c97d288594d25090e5f")})
        self.assertEqual(1, game["Turn"])

    def test_AI_Evaluator_WhenMoveAttackIsPossible_ThenItShouldBeChosen(self):

        test_file = open("tests/AI_Evaluator_WhenAttackIsAvailable_ThenChooseIt.txt", "r")
        gamestate = self.parse_test_case(test_file)

        action = gamestate.current_player().ai.select_action(gamestate)

        self.assertTrue(re.search(".*attack.*", str(action)), "The ai did not choose to attack")

    def test_AI_Evaluator_WhenNoActionsAreAvailable_ThenReduceActionsToZero(self):

        test_file = open("tests/AI_Evaluator_WhenNoActionsAreAvailable_ThenReduceActionsToZero.txt", "r")
        gamestate = self.parse_test_case(test_file)

        action = gamestate.current_player().ai.select_action(gamestate)

        gamestate.do_action(action)

        self.assertEquals(0, gamestate.get_actions_remaining(), "There are too many actions left")

    def assert_equal_documents(self, expected, actual):
        pretty_printer = PrettyPrinter()
        pretty_documents = "Expected:\n" + pretty_printer.pformat(expected) \
                           + "\nActual:\n" + pretty_printer.pformat(actual)
        self.assertEqual(expected, actual, "The document was mangled.\n\n" + pretty_documents)

    def parse_test_case(self, test_file):

        self.assertTrue(re.search('^== [A-Za-z0-9-_]+ ==\r?\n$', test_file.readline()),
                        "Please begin test specification with '== Test_Name =='")

        match = re.search("^Turn: ([1-9][0-9]*)\r?\n$", test_file.readline())
        self.assertTrue(match, "Incorrent turn specification. Please write Turn: [1..]")
        turn = int(match.group(1))

        match = re.search('^Actions: ([0-2])\r?\n$', test_file.readline())
        self.assertTrue(match, "Incorrect action specification. Please write 'Actions: [0..2]'")
        actions_remaining = int(match.group(1))

        player1, player1_units = self.parse_player(test_file)
        player2, player2_units = self.parse_player(test_file)

        gamestate = Gamestate(player1, player1_units, player2, player2_units, turn, actions_remaining)

        self.assertNotEqual("Human", gamestate.current_player().ai, "Active player is a human. It should be a computer")

        return gamestate

    def parse_player(self, test_file):
        self.assertTrue(re.search('^Player(1|2):\r?\n$', test_file.readline()),
                        "Incorrect player specification. Please write: Player1/Player2")

        match = re.search("^(Red|Green)\r?\n$", test_file.readline())
        self.assertTrue(match, "Incorrect player color specification. Please write: Red/Green")
        player = Player(match.group(1))

        match = re.search('^([A-Za-z]+)\r?\n', test_file.readline())
        self.assertTrue(match, "Incorrect player specification. Please write either Human or a named AI")
        player.ai_name = match.group(1)
        if match.group(1) == "Human":
            player.ai = match.group(1)
        else:
            player.ai = ai_module.AI(match.group(1))

        match = re.search('^Extra action: (True|False)\r?\n$', test_file.readline())
        self.assertTrue(match, "Incorrect extra action specification. Please write 'Extra action: True/False'")
        if match.group(1) == "True":
            player.extra_action = True

        self.assertTrue(re.search("\r?\n", test_file.readline()), "Please wrap unit specifications in empty lines")

        units = {}
        line = test_file.readline()
        while line != "" and line != "\r\n" and line != "\n":
            match = re.search("^([A-E][0-8])\r?\n$", line)
            self.assertTrue(match, "Incorrect unit specification. Please write something like 'A1<newline>Archer'")

            position = (ord(match.group(1)[0]) - 64, int(match.group(1)[1]))

            line = test_file.readline()
            match = re.search("^([A-Za-z -_]+)\r?\n$", line)

            units[position] = getattr(units_module, match.group(1))()

            match = re.search("^\r?\n$", test_file.readline())
            self.assertTrue(match, "Please wrap unit specifications in empty lines")
            line = test_file.readline()

        return player, units

    def get_test_gamestate_document(self):
        now = datetime.utcnow()

        return {
            "player1_intelligence": "Human",
            "player2_intelligence": "Human",
            "turn": 1,
            "actions_remaining": 1,
            "extra_action": False,
            "player1_units":
            {
                "D6":
                {
                    "name": "Heavy Cavalry",
                    "attack_counters": 1,
                    "experience": 1
                }
            },
            "player2_units":
            {
                "C7": "Royal Guard",
                "E7": "Archer"
            },
            "created_at": now
        }

if __name__ == "__main__":
    unittest.main()
