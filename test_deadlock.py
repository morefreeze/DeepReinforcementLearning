'''Test is there a deadlock'''
from tqdm import tqdm
from game import *

if __name__ == '__main__':
    for _ in tqdm(range(1000)):
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
            continue
