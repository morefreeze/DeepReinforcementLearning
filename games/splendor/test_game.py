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
            ps = PickStones(g.playerTurn, Stones({color: 2}))
            ps.apply(b)
        ss = b[Position.STONE]
        self.assertTrue(all([ss[Color(c)] == 5 for c in Color.ALL.value]))

    def test_pick_stones2(self):
        g, b, c = self.g, self.b, self.c
        b[Position.STONE] = Stones({Color.WHITE: 2, Color.BLACK: 1})
        ps = PickStones(g.playerTurn, Stones({Color.WHITE: 1, Color.BLACK: 1}))
        self.assertTrue(ps.is_playable(b))
        ps.apply(b)
        ps = PickStones(g.playerTurn, Stones({Color.WHITE: 1}))
        self.assertTrue(ps.is_playable(b))
        ps.apply(b)
        ps = PickStones(g.playerTurn, Stones({Color.WHITE: 1}))
        self.assertFalse(ps.is_playable(b))

    def test_pick_stones3(self):
        g, b, c = self.g, self.b, self.c
        b[Position.STONE] = Stones({Color.WHITE: 5})
        ps = PickStones(g.playerTurn, Stones({Color.WHITE: 2}))
        self.assertTrue(ps.is_playable(b))
        ps.apply(b)
        ps = PickStones(g.playerTurn, Stones({Color.WHITE: 2}))
        self.assertFalse(ps.is_playable(b))

    def test_pick_card(self):
        g, b, c = self.g, self.b, self.c
        pc = PickCard(g.playerTurn, Card(0, Color.WHITE, Stones()))
        self.assertFalse(pc.is_playable(b))
        pc = PickCard(g.playerTurn, c)
        self.assertFalse(pc.is_playable(b))

    def test_pick_card2(self):
        g, b, c = self.g, self.b, self.c
        p = g.current_player
        c.need = Stones({Color.WHITE: 3})
        p[PlayerElement.STONE] = Stones({Color.WHITE: 4, Color.GOLD: 2})
        pc = PickCard(g.playerTurn, c)
        self.assertTrue(pc.is_playable(b))
        pc.apply(b)
        self.assertDictEqual(p[PlayerElement.STONE], Stones({Color.WHITE: 1, Color.GOLD: 2}))
        self.assertEqual(len(p.binary(b)), 160)

    def test_pick_card3(self):
        g, b, c = self.g, self.b, self.c
        p = g.current_player
        c.need = Stones({Color.WHITE: 3})
        p[PlayerElement.STONE] = Stones({Color.WHITE: 1, Color.GOLD: 3})
        pc = PickCard(g.playerTurn, c)
        self.assertTrue(pc.is_playable(b))
        pc.apply(b)
        self.assertDictEqual(p[PlayerElement.STONE], Stones({Color.GOLD: 1}))
        self.assertEqual(len(p.binary(b)), 160)

    def test_fold_card(self):
        g, b, c = self.g, self.b, self.c
        fc = FoldCard(g.playerTurn, c)
        self.assertTrue(fc.is_playable(b))
        fc.apply(b)
        self.assertFalse(fc.is_playable(b))
        fc = FoldCard(g.playerTurn, b[Position.LINE1][0])
        self.assertTrue(fc.is_playable(b))
        fc.apply(b)
        fc = FoldCard(g.playerTurn, b[Position.LINE1][0])
        self.assertTrue(fc.is_playable(b))
        fc.apply(b)
        pc = PickCard(g.playerTurn, c)
        self.assertFalse(pc.is_playable(b))
        c.need = Stones({Color.WHITE: 3})
        pc = PickCard(g.playerTurn, c)
        self.assertTrue(pc.is_playable(b))
        pc.apply(b)
        # Can't pick fold card twice
        pc = PickCard(g.playerTurn, c)
        self.assertFalse(pc.is_playable(b))

    def test_pick_noble(self):
        g, b, c = self.g, self.b, self.c
        p = g.current_player
        noble = b[Position.HALL][0]
        noble.need = Stones({Color.WHITE: 1})
        noble.score = 3
        c.color = Color.WHITE
        c.need = Stones()
        c.score = 2
        self.assertEqual(p.score, 0)
        pc = PickCard(g.playerTurn, c)
        self.assertTrue(pc.is_playable(b))
        pc.apply(b)
        self.assertEqual(p.score, 5)
        self.assertEqual(len(p.binary(b)), 160)

    def test_do_nothing(self):
        g, b, c = self.g, self.b, self.c
        b[Position.STONE] = Stones()
        b[Position.LINE1] = []
        b[Position.LINE2] = []
        b[Position.LINE3] = []
        gs = GameState(b, 0)
        self.assertEqual(gs.allActions[gs.allowedActions[0]].typ, ActionType.DO_NOTHING)

    def test_not_your_turn(self):
        g, b = self.g, self.b
        ps = PickStones(g.playerTurn, Stones({Color.WHITE: 1}))
        self.assertTrue(ps.is_playable(b))
        ps = PickStones(g.playerTurn+1, Stones({Color.WHITE: 1}))
        self.assertFalse(ps.is_playable(b))


class TestGameState(unittest.TestCase):
    def setUp(self):
        self.g = Game(player_num=4, seed=0)
        self.gs = self.g.gameState

    def test_all_actions(self):
        gs = self.gs
        ac = gs.allActions
        self.assertEqual(len(ac), 844)

    def test_end_game(self):
        b = self.g.board
        p = self.g.current_player
        self.assertFalse(p.win())
        for _ in range(5):
            c = b[Position.LINE3][0]
            p[PlayerElement.CARD].append(c)
            b.draw(c)
        self.assertGreater(p.score, 15)
        self.assertTrue(p.win())
        gs = GameState(b, self.g.playerTurn)
        # Need to finish fairTurn
        self.assertEqual(gs.isEndGame, 0)
        gs = GameState(b, 3)
        self.assertEqual(gs.isEndGame, 1)

if __name__ == '__main__':
    unittest.main()
