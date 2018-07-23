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

    def test_pick_card(self):
        g, b, c = self.g, self.b, self.c
        pc = PickCard(g.current_player, Card(Color.WHITE, Stones()))
        self.assertFalse(pc.is_playable(b))
        pc = PickCard(g.current_player, c)
        self.assertFalse(pc.is_playable(b))

    def test_fold_card(self):
        # todo
        pass

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.g = Game(player_num=4, seed=0)
        self.gs = self.g.state

    def test_allowed_actions(self):
        gs = self.gs
        ac = gs.allowedActions
        self.assertEqual(len(ac), 30 + 15)  # PickStones(30) + FoldCard(15)
        self.assertTrue(all([isinstance(x, PickStones) for x in ac[:30]]))
        self.assertTrue(all([isinstance(x, FoldCard) for x in ac[30:]]))

    def test_end_game(self):
        b = self.g.board
        p = self.g.player
        self.assertFalse(p.win())
        for _ in range(5):
            c = b[Position.LINE3][0]
            p[GameElement.CARD].append(c)
            b.draw(c)
        self.assertGreater(p.score, 15)
        self.assertTrue(p.win())
        gs = GameState(b, self.g.players, self.g.current_player)
        # Need to finish fairTurn
        self.assertEqual(gs.isEndGame, 0)
        gs = GameState(b, self.g.players, 3)
        self.assertEqual(gs.isEndGame, 1)

if __name__ == '__main__':
    unittest.main()
