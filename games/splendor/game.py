# coding: utf-8
import random
import itertools
from enum import Enum, auto

MAX_STONES = 10

class Color(Enum):
    UNKNOWN = -1
    GOLD = 0
    WHITE = 1
    BLUE = 2
    GREEN = 3
    RED = 4
    BLACK = 5
    ALL = [WHITE, BLUE, GREEN, RED, BLACK]

class GameElement(Enum):
    STONE = 0
    CARD = 1
    NOBLE = 2
    FOLD = 3

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
    STONE = 9  # Stones stay here if they are present

class ActionType(Enum):
    PICK_STONES = auto()
    PICK_CARD = auto()
    PICK_NOBLE = auto()
    FOLD_CARD = auto()

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
            if not (k in other and v <= other[k]):
                return False
        return True

    def __sub__(self, rhs):
        assert(rhs <= self)
        for k in self:
            self[k] -= rhs[k]
        return self

class Stone(object):
    color = Color.UNKNOWN
    num = 0
    where = Position.OUT_OF_GAME

    def __init__(self, color, num, where):
        self.color, self.num, self.where = color, num, where

    def __str__(self):
        return '%s %s on %s' % (self.color, self.num, self.where)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)

class Card(Stone):
    score = 0
    # List of Stone
    need = Stones()

    def __init__(self, color, need, score=0):
        self.color = color
        if type(need) == dict:
            need = Stones(need)
        self.need = need
        self.score = score

    def __str__(self):
        return '%s->%s %s' % ({st: num for st, num in self.need.items() if num > 0}, self.color, self.score)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)

    def fulfill(self, stones, cards) -> (bool, dict):
        '''return (is_fulfill, removed_stones)
        return True if card can be fulfill and give what should be paid
        paid order must be cards, stones, golds
        '''
        has_stones = Stones()
        removed_stones = Stones()
        for card in cards:
            has_stones[card.color] += card.num
        for c in self.need:
            if self.need[c] > has_stones[c] and stones[c] > 0:
                removed_stones[c] += min(stones[c], self.need[c] - has_stones[c])
                has_stones[c] += removed_stones[c]
        need_golds = 0
        for k, v in self.need.items():
            if k == Color.GOLD:
                assert(v == 0)
                continue
            if v - has_stones[k] > 0:
                if stones[Color.GOLD] < v - has_stones[k]:
                    return False, None
                removed_stones[Color.GOLD] += v - has_stones[k]
        return True, removed_stones

class Cards(dict):
    '''List all cards'''
    def __init__(self):
        deck1_patterns = [
            ((0, 1, 2, 1, 1), 0),
            ((0, 2, 2, 0, 1), 0),
            ((3, 1, 0, 0, 1), 0),  # This pat is not disciplinary
            ((0, 2, 0, 0, 2), 0),  # This pat is not disciplinary
            ((0, 1, 1, 1, 1), 0),
            ((0, 0, 4, 0, 0), 0),
            ((0, 3, 0, 0, 0), 0),  # This pat is not disciplinary
            ((0, 0, 0, 2, 1), 0),
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
        for deck, patterns in [
            (Position.DECK1, deck1_patterns),
            (Position.DECK2, deck2_patterns),
            (Position.DECK3, deck3_patterns),
        ]:
            self[deck] = []
            for pat, score in patterns:
                for i in range(5):
                    self[deck].append(
                        Card(Color(Color.ALL.value[i]),
                             dict(zip(map(Color, (Color.ALL.value*2)[i:i+5]), pat)),
                            score)
                    )

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

    def __str__(self):
        return '%s->%s' % ({st: num for st, num in self.need.items() if num > 0}, self.score)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)

    def fulfill(self, cards) -> bool:
        has_stones = Stones()
        for c in cards:
            has_stones[c.color] += 1
        return self.need <= has_stones

class Nobles(list):
    '''List all noble cards'''
    def __init__(self):
        for i in range(5):
            self.append(Noble(dict(zip(map(Color, (Color.ALL.value*2)[i:i+3]), [3,3,3])), score=4))
        for i in range(5):
            self.append(Noble(dict(zip(map(Color, (Color.ALL.value*2)[i:i+2]), [4,4])), score=3))

class Player(dict):

    def __init__(self):
        super().__init__()
        self[GameElement.STONE] = Stones()
        self[GameElement.CARD] = []
        self[GameElement.NOBLE] = []
        self[GameElement.FOLD] = []

    def win(self):
        return self.score >= 15

    @property
    def score(self):
        score = 0
        for ele in (GameElement.CARD, GameElement.NOBLE):
            score += sum([c.score for c in self[ele]])
        return score

class Board(dict):

    def __init__(self, player_num=4):
        super().__init__()
        # Each color stones is 4, 5, 7 for 2-4 players respectively
        init_stones = {
            2: Stones({Color.GOLD: 5, Color.WHITE: 4, Color.BLUE: 4, Color.GREEN: 4, Color.RED: 4, Color.BLACK: 4}),
            3: Stones({Color.GOLD: 5, Color.WHITE: 5, Color.BLUE: 5, Color.GREEN: 5, Color.RED: 5, Color.BLACK: 5}),
            4: Stones({Color.GOLD: 5, Color.WHITE: 7, Color.BLUE: 7, Color.GREEN: 7, Color.RED: 7, Color.BLACK: 7}),
        }
        self[Position.STONE] = init_stones[player_num]
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

    def draw(self, card):
        '''Remove card from some line and draw new card from deck'''
        for deck, line in [
            (Position.DECK1, Position.LINE1),
            (Position.DECK2, Position.LINE2),
            (Position.DECK3, Position.LINE3),
        ]:
            if card in self[line]:
                self[line].remove(card)
                self._trans(deck, line)

    def _trans(self, from_, to):
        if len(self[from_]) > 0:
            self[to].append(self[from_][0])
            self[from_] = self[from_][1:]

class Action(object):

    def __init__(self, playerTurn, typ, card_or_stone):
        self.playerTurn = playerTurn
        self.typ = typ
        self.card_or_stone = card_or_stone

    def __str__(self):
        return 'Player %s do %s with %s' % (self.playerTurn, self.typ, self.card_or_stone)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)

    def apply(self, board):
        raise NotImplementedError

    def is_playable(self, board):
        return False

class PickStonesExceedError(Exception):
    pass

class PickStones(Action):

    def __init__(self, playerTurn, stone):
        super().__init__(playerTurn, ActionType.PICK_STONES, stone)

    def is_playable(self, board):
        stones = self.card_or_stone
        if stones[Color.GOLD] > 0:
            return False
        colors = [c for c in stones if c != Color.GOLD and stones[c] > 0]
        if len(colors) == 0:
            return True
        elif len(colors) == 1:
            return board[Position.STONE][colors[0]] >= 4
        elif len(colors) <= 3:
            return all([board[Position.STONE][c] for c in colors])
        else:
            return False

    def apply(self, board):
        if not self.is_playable(board):
            raise PickStonesExceedError
        player = board[Position.PLAYER_POS][self.playerTurn]
        stones = self.card_or_stone
        for c, num in stones.items():
            board[Position.STONE][c] -= num
            player[GameElement.STONE][c] += num

class NotFulfillError(Exception):
    pass

class PickCard(Action):

    def __init__(self, playerTurn, card):
        super().__init__(playerTurn, ActionType.PICK_CARD, card)

    def is_playable(self, board):
        player = board[Position.PLAYER_POS][self.playerTurn]
        card = self.card_or_stone
        in_line = any([card in board[line] for line in [Position.LINE1, Position.LINE2, Position.LINE3]])
        return in_line and card.fulfill(player[GameElement.STONE], player[GameElement.CARD])[0]

    def apply(self, board):
        player = board[Position.PLAYER_POS][self.playerTurn]
        card = self.card_or_stone
        is_fulfill, removed_stones = card.fulfill(player[GameElement.STONE], player[GameElement.CARD])
        if not is_fulfill:
            raise NotFulfillError
        player[GameElement.STONE] -= removed_stones
        player[GameElement.CARD].append(card)
        board.draw(card)
        # If fulfill noble then acquire automatically
        for noble in board[Position.HALL]:
            if noble.fulfill(player[GameElement.CARD]):
                pn = PickNoble(self.playerTurn, ActionType.PICK_NOBLE, noble)
                pn.apply(b)

class PickNoble(Action):

    def __init__(self, playerTurn, noble):
        super().__init__(playerTurn, ActionType.PICK_NOBLE, noble)

    def is_playable(self, board):
        player = board[Position.PLAYER_POS][self.playerTurn]
        noble = self.card_or_stone
        return noble in board[Positio.HALL] and noble.fulfill(player[GameElement.CARD])

    def apply(self, board):
        if self.is_playable(board):
            player = board[Position.PLAYER_POS][self.playerTurn]
            noble = self.card_or_stone
            board[Position.HALL].remove(noble)
            player[GameElement.NOBLE].append(noble)

class FoldCard(Action):

    def __init__(self, playerTurn, card):
        super().__init__(playerTurn, ActionType.FOLD_CARD, card)

    def is_playable(self, board):
        # todo: Now only fold card which is present, however first card from deck is able to fold
        player = board[Position.PLAYER_POS][self.playerTurn]
        card = self.card_or_stone
        in_line = any([card in board[line] for line in [Position.LINE1, Position.LINE2, Position.LINE3]])
        return in_line and len(player[GameElement.FOLD]) < 3

    def apply(self, board):
        if not self.is_playable(board):
            raise NotFulfillError
        player = board[Position.PLAYER_POS][self.playerTurn]
        card = self.card_or_stone
        player[GameElement.FOLD].append(card)
        if board[Position.STONE][Color.GOLD] > 0:
            board[Position.STONE][Color.GOLD] -= 1
            player[GameElement.STONE][Color.GOLD] += 1
        board.draw(card)

class Game(object):

    def __init__(self, player_num=4, seed=None):
        self.name = 'splendor'
        self.player_num = player_num
        self.seed = seed
        self.reset()
        self.pieces = {'0': 'Alice', '1': 'Bob', '2': 'Claire', '3': 'Doggy'}
        self.grid_shape = (1, 100)
        self.input_shape = (player_num, 1, len(self.gameState.allowedActions))
        self.state_size = len(self.gameState.binary)
        self.action_size = 60


    def reset(self):
        self.playerTurn = 0
        random.seed(self.seed)
        self.board = Board(self.player_num)
        self.players = self.board[Position.PLAYER_POS]
        self.gameState = GameState(self.board, self.playerTurn)
        return self.gameState

    def step(self, action):
        new_state, value, done = self.gameState.takeAction(action)
        self.gameState = new_state
        self.playerTurn = new_state.playerTurn
        info = None
        return ((new_state, value, done, info))

    @property
    def player(self):
        return self.board[Position.PLAYER_POS][self.playerTurn]

class GameState(object):

    def __init__(self, board, playerTurn):
        self.board = board
        self.players = board[Position.PLAYER_POS]
        self.playerTurn = playerTurn
        self.binary = self._binary()
        self.id = self._convertStateToId()
        self.allowedActions = self._allowedActions()
        self.fairTurn = False
        self.isEndGame = self._checkForEndGame()
        self.value = self._getValue()
        self.score = self._getScore()

    def _binary(self):
        return tuple(map(str, [self.board, self.players, self.playerTurn]))

    def _convertStateToId(self):
        return '|'.join(self.binary)

    def _allowedActions(self):
        allowed_actions = []
        # PickStones
        # Pick 1 stone from each color
        for num in range(3, 0, -1):
            for colors in itertools.combinations(Color.ALL.value, num):
                ps = PickStones(self.playerTurn, Stones({Color(c): 1 for c in colors}))
                if ps.is_playable(self.board):
                    allowed_actions.append(ps)
        # Pick 2 stones from one color
        for c in Color.ALL.value:
            ps = PickStones(self.playerTurn, Stones({Color(c): 2}))
            if ps.is_playable(self.board):
                allowed_actions.append(ps)
        # PickCard & FoldCard
        for line in (Position.LINE1, Position.LINE2, Position.LINE3):
            for card in self.board[line]:
                pc = PickCard(self.playerTurn, card)
                if pc.is_playable(self.board):
                    allowed_actions.append(pc)
                pf = FoldCard(self.playerTurn, card)
                if pf.is_playable(self.board):
                    allowed_actions.append(pf)
        return allowed_actions

    def _checkForEndGame(self):
        for p in self.board[Position.PLAYER_POS]:
            if p.win():
                self.fairTurn = True
        if self.fairTurn and self.playerTurn == len(self.board[Position.PLAYER_POS]) - 1:
            return 1
        return 0

    def _getValue(self):
        # todo: sum all player score, if someone wins, return (-1, -1, 1) else (0, 0, 0)
        # Maybe return score directly?
        return (0, 0, 0)

    def _getScore(self):
        tmp = self.value
        return (tmp[1], tmp[2])

    def takeAction(self, action):
        action.apply(self.board)
        self.playerTurn = (self.playerTurn + 1) % len(self.players)
        new_state = GameState(self.board, self.playerTurn)
        value, done = (new_state.value[0], 1) if new_state.isEndGame else (0, 0)
        return new_state, value, done

    def render(self, logger):
        logger.info('-'*20)

if __name__ == '__main__':
    g = Game(player_num=4, seed=0)
    b = g.board
    gs = g.gameState
    g.step(gs.allowedActions[-1])

    p = g.player
    for _ in range(5):
        c = b[Position.LINE3][0]
        p[GameElement.CARD].append(c)
        b.draw(c)
    print(p.score)
