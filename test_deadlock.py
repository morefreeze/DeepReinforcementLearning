'''Test is there a deadlock'''
import multiprocessing
from game import *

def f():
    seed = random.randrange(sys.maxsize)
    g = Game(player_num=2, seed=seed)
    gs = g.gameState
    b = g.board
    try:
        for i in range(300):
            action = random.choice(gs.allowedActions)
            gs, value, done, info = g.step(action)
            if done == 1:
                break
        else:
            print("Sth must be deadlock {}".format(seed))
            raise RuntimeError
    except RuntimeError as e:
        raise e
    except:
        pass

if __name__ == '__main__':
    with multiprocessing.Pool(5) as p:
        res = [p.apply_async(f) for _ in range(100)]
        list(map(lambda x: x.get(), res))
