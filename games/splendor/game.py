# coding: utf-8
import random
from enum import Enum

class Color(Enum):
    UNKNOWN = -1
    GOLD = 0
    WHITE = 1
    BLUE = 2
    GREEN = 3
    RED = 4
    BLACK = 5
    ALL = [WHITE, BLUE, GREEN, RED, BLACK]

# Game Element
class GameElement(Enum):
    STONE = 0
    CARD = 1
    NOBLE = 2
    PLAYER = 3

# Position
class Position(Enum):
    OUT_OF_GAME = 0  # Noble who are not present
    DECK1 = 1
    DECK2 = 2
    DECK3 = 3
    LINE1 = 4
    LINE2 = 5
    LINE3 = 6
    PLAYER_POS = 7
    HALL = 8  # Noble stay here if they are present
    TABLE = 9  # Stones stay here if they are present

class Stones(dict):

    def __init__(self, other=None):
        super().__init__({
            Color.GOLD: 0,
            Color.WHITE: 0,
            Color.BLUE: 0,
            Color.GREEN: 0,
            Color.RED: 0,
            Color.BLACK: 0,
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
    color = Color.UNKNOWN
    num = 0
    where = Position.OUT_OF_GAME

    def __init__(self, color, num, where):
        self.color, self.num, self.where = color, num, where

    def __str__(self):
        return 

class Card(Stone):
    score = 0
    # List of Stone
    need = Stones()

    def __init__(self, need, score=0):
        if type(need) == dict:
            need = Stones(need)
        self.need = need
        self.score = score

    def __str__(self):
        return '%s->%s' % (self.need, self.score)

    def __repr__(self):
        return 'Card(%s->%s)' % (self.need, self.score)

    def is_fulfill(self, stones):
        has_stones = Stones()
        for s in stones:
            has_stones[s.color] += s.num
        if self.need <= has_stones:
            return True
        need_golds = 0
        for k, v in need.items():
            if k == Color.GOLD:
                assert(v == 0)
                continue
            need_golds += min(0, v - has_stones[k])
        return need_golds <= has_stones[Color.GOLD]

class Cards(dict):
    '''List all cards'''
    def __init__(self):
        deck1_patterns = [
            (0, 1, 2, 1, 1),
            (0, 2, 2, 0, 1),
            (3, 1, 0, 0, 1),  # This pat is not disciplinary
            (0, 2, 0, 0, 2),  # This pat is not disciplinary
            (0, 1, 1, 1, 1),
            (0, 0, 4, 0, 0),
            (0, 3, 0, 0, 0),  # This pat is not disciplinary
            (0, 0, 0, 2, 1),
        ]
        deck2_patterns = [
            ((5, 3, 0, 0, 0), 2),  # colors number, score
            ((0, 0, 1, 4, 2), 2),
            ((0, 0, 3, 2, 2), 2),  # This pat is not disciplinary
            ((6, 0, 0, 0, 0), 2),
            ((5, 0, 0, 0, 0), 2),  # This pat is not disciplinary
            ((2, 3, 0, 3, 0), 1),
        ]
        deck3_patterns = [
            ((3, 0, 0, 0, 7), 5),
            ((3, 0, 0, 3, 6), 4),
            ((0, 0, 0, 0, 7), 4),
            ((0, 3, 3, 5, 3), 3),
        ]
        self[Position.DECK1] = []
        for pat in deck1_patterns:
            for i in range(5):
                self[Position.DECK1].append(Card(dict(zip((Color.ALL.value*2)[i:i+5], pat))))
        self[Position.DECK2] = []
        for pat, score in deck2_patterns:
            for i in range(5):
                self[Position.DECK2].append(Card(dict(zip((Color.ALL.value*2)[i:i+5], pat)), score))
        self[Position.DECK3] = []
        for pat, score in deck3_patterns:
            for i in range(5):
                self[Position.DECK3].append(Card(dict(zip((Color.ALL.value*2)[i:i+5], pat)), score))

class CardStone(Stone):
    '''CardStone is a collections of cards, but it refer Stone attribute(color, num)'''

class Noble(object):
    score = 0
    # List of CardType
    need = Stones()

    def __init__(self, need, score=3):
        if type(need) == dict:
            need = Stones(need)
        self.need = need
        self.score = score

    def is_fulfill(self, cards):
        has_stones = Stones()
        for c in cards:
            has_stones[c.color] += 1
        return self.need <= has_stones

class Nobles(list):
    '''List all noble cards'''
    def __init__(self):
        for i in range(5):
            self.append(Noble(dict(zip((Color.ALL.value*2)[i:i+3], [3,3,3])), score=4))
        for i in range(5):
            self.append(Noble(dict(zip((Color.ALL.value*2)[i:i+2], [4,4])), score=3))

class Player(dict):

    def __init__(self):
        super().__init__()
        self[GameElement.STONE] = Stones()
        self[GameElement.CARD] = []
        self[GameElement.NOBLE] = []

class Board(dict):

    def __init__(self, player_num=4):
        super().__init__()
        # Each color stones is 4, 5, 7 for 2-4 players respectively
        init_stones = {
            2: Stones({Color.GOLD: 5, Color.WHITE: 4, Color.BLUE: 4, Color.GREEN: 4, Color.RED: 4, Color.BLACK: 4}),
            3: Stones({Color.GOLD: 5, Color.WHITE: 5, Color.BLUE: 5, Color.GREEN: 5, Color.RED: 5, Color.BLACK: 5}),
            4: Stones({Color.GOLD: 5, Color.WHITE: 7, Color.BLUE: 7, Color.GREEN: 7, Color.RED: 7, Color.BLACK: 7}),
        }
        self[Position.TABLE] = init_stones[player_num]
        cards = Cards()
        self[Position.DECK1] = random.sample(cards[Position.DECK1], len(cards[Position.DECK1]))
        self[Position.DECK2] = random.sample(cards[Position.DECK2], len(cards[Position.DECK2]))
        self[Position.DECK3] = random.sample(cards[Position.DECK3], len(cards[Position.DECK3]))
        # Each deck 4 cards, 5 cards for 4 players
        draw_num = 5 if player_num == 4 else 4
        self[Position.LINE1], self[Position.DECK1] = self[Position.DECK1][:draw_num], self[Position.DECK1][draw_num:]
        self[Position.LINE2], self[Position.DECK2] = self[Position.DECK2][:draw_num], self[Position.DECK2][draw_num:]
        self[Position.LINE3], self[Position.DECK3] = self[Position.DECK3][:draw_num], self[Position.DECK3][draw_num:]

        nobles = Nobles()
        random.shuffle(nobles)
        # Draw player_num+1 noble cards
        self[Position.HALL] = nobles[:player_num+1]
        self[Position.OUT_OF_GAME] = nobles[player_num+1:]
        self[Position.PLAYER_POS] = [Player() for _ in range(player_num)]

class Game(object):

    def __init__(self, player_num=4, seed=None):
        self.current_player = 0
        self.player_num = player_num
        self.name = 'splendor'
        self.seed = seed

        self.reset()

    def reset(self):
        random.seed(self.seed)
        self.board = Board(self.player_num)
        self.players = self.board[Position.PLAYER_POS]
        self.state = GameState(self.board, self.players, self.current_player)

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
        return ''

    def _convertStateToId(self):
        # todo
        return 0

    def _allowedActions(self):
        # todo
        return []

    def _checkForEndGame(self):
        # todo
        return False

    def _getValue(self):
        # todo: sum all player score, if someone wins, return (-1, -1, 1) else (0, 0, 0)
        # Maybe return score directly?
        return (0, 0, 0)

    def _getScore(self):
        tmp = self.value
        return (tmp[1], tmp[2])
