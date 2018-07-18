import unittest
from game import *

class TestSetup(unittest.TestCase):
    def test_player_num(self):
        g = Game(player_num=2)
        assert len(g.board[Position.PLAYER_POS]) == 2
        g = Game(player_num=3)
        assert len(g.board[Position.PLAYER_POS]) == 3
        g = Game(player_num=4)
        assert len(g.board[Position.PLAYER_POS]) == 4

class TestGame(unittest.TestCase):
    def setUp(self):
        self.g = Game(player_num=4)

    def test_setup(self):
        g = self.g
        b = g.board
        ss = b[Position.STONE]
        assert all([len(b[x]) == 5 for x in (Position.LINE1, Position.LINE2, Position.LINE3)])
        assert all([ss[Color(c)] == 7 for c in Color.ALL.value])

class TestAction(unittest.TestCase):
    def setUp(self):
        self.g = Game(player_num=4)
        self.b = self.g.board
        self.c = self.g.board[Position.LINE1][0]

    def test_pick_stones(self):
        g, b, c = self.g, self.b, self.c
        for cv in Color.ALL.value:
            color = Color(cv)
            ps = PickStones(g.current_player, Stones({color: 2}))
            ps.apply(b)
        ss = b[Position.STONE]
        assert all([ss[Color(c)] == 5 for c in Color.ALL.value])

if __name__ == '__main__':
    unittest.main()
