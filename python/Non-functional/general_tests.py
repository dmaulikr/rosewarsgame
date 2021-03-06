import unittest
from datetime import datetime
from gamestate import Gamestate
from pymongo import MongoClient
from bson.objectid import ObjectId
import action_getter
from action import Action
from gamestate_library import document_to_string


class TestAI(unittest.TestCase):

    def test_GamestateDocument_WhenSavingAndLoading_ThenItShouldBeTheSame(self):
        document = self.get_test_gamestate_document()
        gamestate = Gamestate.from_document(document)
        same_document = gamestate.to_document()

        self.assert_equal_documents(document, same_document)

    def test_ActionDocument_WhenSavingAndLoading_ThenItShouldBeTheSame(self):
        gamestate = Gamestate.from_document(self.get_test_gamestate_document())
        actions = action_getter.get_actions(gamestate)
        for action in actions:
            action_document = action.to_document()
            same_action = Action.from_document(gamestate.all_units(), action_document)
            same_action.created_at = action.created_at
            same_action_document = same_action.to_document()

            self.assertEquals(action, same_action)
            self.assertEquals(action_document, same_action_document)

    def test_IfBoardIsFlippedTwoTimes_ThenItShouldBeTheSame(self):
        gamestate = Gamestate.from_document(self.get_test_gamestate_document())
        gamestate_copy = Gamestate.from_document(self.get_test_gamestate_document())
        gamestate_copy.created_at = gamestate.created_at
        gamestate_copy.flip_all_units()
        gamestate_copy.flip_all_units()

        self.assert_equal_documents(gamestate.to_document(), gamestate_copy.to_document())
        self.assertEqual(gamestate, gamestate_copy)

    def test_pymongo_WhenAGameIsInTheDatabase_ThenWeShouldBeAbleToFindIt(self):
        client = MongoClient(host="server.rosewarsgame.com")
        database = client.unnamed
        games = database.games

        game = games.find_one({"_id": ObjectId("51e86e5fea5a8f135cbc0326")})
        self.assertEqual(1, game["Turn"])

    def assert_equal_documents(self, expected, actual):
        documents = "Expected:\n" + common.document_to_string(expected)
        documents += "\nActual:\n" + common.document_to_string(actual)
        self.assertEqual(expected, actual, "The document was wrong.\n\n" + documents)

    def get_test_gamestate_document(self):
        now = datetime.utcnow()

        return {
            "actions_remaining": 1,
            "player1_units": {
                "D6": {
                    "name": "Ballista",
                    "experience": 1,
                    "attack_skill": 1
                },
                "D8": "Saboteur"
            },
            "player2_units": {
                "C7": {
                    "name": "Royal Guard",
                    "experience": 3
                },
                "E7": "Archer"
            },
            "created_at": now
        }

if __name__ == "__main__":
    unittest.main()
