# coding: utf-8
import random

# Stone Type
UNKNOWN = -1
GOLD = 0
WHITE = 1
BLUE = 2
GREEN = 3
RED = 4
BLACK = 5

# Game Element
STONE = 0
CARD = 1
PEOPLE = 2
PLAYER = 3
CARD_DECK = 4


class Stones(dict):

    def __init__(self, other=None):
        super().__init__({
            GOLD: 0,
            WHITE: 0,
            BLUE: 0,
            GREEN: 0,
            RED: 0,
            BLACK: 0,
        })
        if other:
            for k, v in other.items():
                if k not in self:
                    continue
                self[k] += v

    def __le__(self, other):
        for k, v in self.items():
            if not (k in other and v < other[k]):
                return False
        return True


class Stone(object):
    color = UNKNOWN
    num = 0

    def __init__(self, color, num):
        self.color, self.num = color, num

class Card(Stone):
    score = 0
    # List of Stone
    need = Stones()

    def is_fulfill(self, stones):
        has_stones = Stones()
        for s in stones:
            has_stones[s.color] += s.num
        if self.need <= has_stones:
            return True
        need_golds = 0
        for k, v in need.items():
            if k == GOLD:
                assert(v == 0)
                continue
            need_golds += min(0, v - has_stones[k])
        return need_golds <= has_stones[GOLD]

class CardStone(Stone):
    '''CardStone is a collections of cards, but it refer Stone attribute(color, num)'''

class People(object):
    score = 0
    # List of CardType
    need = Stones()

    def is_fulfill(self, cards):
        has_stones = Stones()
        for c in cards:
            has_stones[c.color] += 1
        return self.need <= has_stones:

class Player(dict):

    def __init__(self):
        super().__init__()
        self[STONE] = Stones()
        self[CARD] = []
        self[PEOPLE] = []

class Board(dict):

    def __init__(self, player_num=4):
        super().__init__()
        self[STONE] = Stones()
        self[CARD] = [[] for _ in range(3)]
        self[PEOPLE] = [Player() for _ in range(player_num)]


class Game(object):

    def __init__(self, player_num=4, seed=None):
        self.current_player = 0
        self.player_num = player_num
        self.name = 'splendor'
        self.seed = seed

        self.reset()

    def reset(self):
        random.seed(self.seed)
        # todo: fill correct arguments
        self.state = GameState()

class GameState(object):

    def __init__(self, board, players, current_player):
        self.board = board
        self.players = players
        self.current_player = current_player
        self.binary = self._binary()
        self.id = self._convertStateToId()
        self.allowedActions = self._allowedActions()
        self.isEndGame = self._checkForEndGame()
        self.value = self._getValue()
        self.score = self._getScore()

    def _binary(self):
        # todo

    def _convertStateToId(self):
        # todo

    def _allowedActions(self):
        # todo

    def _checkForEndGame(self):
        # todo

    def _getValue(self):
        # todo: sum all player score, if someone wins, return (-1, -1, 1) else (0, 0, 0)
        # Maybe return score directly?

    def _getScore(self):
        tmp = self.value
        return (tmp[1], tmp[2])
