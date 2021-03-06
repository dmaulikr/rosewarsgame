import json
import common
from unittest import TestCase
from game import Game


class ReplayTestCase(TestCase):
    """
    For a given replay file, test if loading up the initial gamestate and
    applying all the actions results in the given (current) gamestate
    """

    def __init__(self, testcase_file):
        super(ReplayTestCase, self).__init__()
        self.testcase_file = testcase_file

    def runTest(self):
        replay_document = json.loads(open(self.testcase_file).read())
        replay_game = Game.from_log_document(replay_document)

        gamestate_document = replay_game.gamestate.to_document()

        common.assert_equal_documents(self, replay_document["gamestate"], gamestate_document, self.testcase_file)
