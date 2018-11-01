import numpy as np
import random

from game import Game, GameState
from model import Residual_CNN

from agent import Agent, User

import config

# todo: multi-player supported
def playMatchesBetweenVersions(env, run_version, player1version, player2version, EPISODES, logger, turns_until_tau0, goes_first = 0):

    if player1version == -1:
        player1 = User('player1', env.state_size, env.action_size)
    else:
        player1_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, env.input_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)

        if player1version > 0:
            player1_network = player1_NN.read(env.name, run_version, player1version)
            player1_NN.model.set_weights(player1_network.get_weights())   
        player1 = Agent('player1', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, player1_NN)

    if player2version == -1:
        player2 = User('player2', env.state_size, env.action_size)
    else:
        player2_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, env.input_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)
        if player2version > 0:
            player2_network = player2_NN.read(env.name, run_version, player2version)
            player2_NN.model.set_weights(player2_network.get_weights())
        player2 = Agent('player2', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, player2_NN)

    scores, memory, points, sp_scores = playMatches(player1, player2, EPISODES, logger, turns_until_tau0, None, goes_first)

    return (scores, memory, points, sp_scores)


BEST_PLAYER_ID = 0
PLAYER_ID1 = 1
PLAYER_ID2 = 2
PLAYER_ID3 = 3
def playMatches(player1, player2, EPISODES, logger, turns_until_tau0, memory = None, goes_first = -1):

    env = Game()
    scores = {player1.name:0, "drawn": 0, player2.name:0}
    sp_scores = {'sp':0, "drawn": 0, 'nsp':0}
    points = {player1.name:[], player2.name:[]}

    for e in range(EPISODES):

        logger.info('====================')
        logger.info('EPISODE %d OF %d', e+1, EPISODES)
        logger.info('====================')

        print (str(e+1) + ' ', end='')

        state = env.reset()

        done = 0
        turn = 0
        player1.mcts = None
        player2.mcts = None

        if goes_first == -1:
            player1Starts = random.randint(0,1)  # todo: player number
        else:
            player1Starts = goes_first

        if player1Starts == 0:
            players = {BEST_PLAYER_ID:{"agent": player1, "name":player1.name}
                    , PLAYER_ID1: {"agent": player2, "name":player2.name}
                    }
        else:
            players = {BEST_PLAYER_ID:{"agent": player2, "name":player2.name}
                    , PLAYER_ID1: {"agent": player1, "name":player1.name}
                    }
        logger.info('--------------')

        env.gameState.render(logger)

        while done == 0:
            turn = turn + 1
            logger.info("TURN %d", turn)

            #### Run the MCTS algo and return an action
            if turn < turns_until_tau0:
                action, pi, MCTS_value, NN_value = players[state.playerTurn]['agent'].act(state, 1)
            else:
                action, pi, MCTS_value, NN_value = players[state.playerTurn]['agent'].act(state, 0)

            if memory != None:
                ####Commit the move to memory
                memory.commit_stmemory(env.identities, state, pi)


            logger.info('action: %d', action)
            # for r in range(env.grid_shape[0]):
                # logger.info(['----' if x == 0 else '{0:.2f}'.format(np.round(x,2)) for x in pi[env.grid_shape[1]*r : (env.grid_shape[1]*r + env.grid_shape[1])]])
            logger.info('MCTS perceived value for %s: %f', state.pieces[str(state.playerTurn)] ,np.round(MCTS_value,2))
            logger.info('NN perceived value for %s: %f', state.pieces[str(state.playerTurn)] ,np.round(NN_value,2))
            logger.info('====================')

            ### Do the action
            state, winner, done, _ = env.step(action) #the value of the newState from the POV of the new playerTurn i.e. -1 if the previous player played a winning move

            env.gameState.render(logger)

            if done == 1:
                if memory != None:
                    #### If the game is finished, assign the values correctly to the game moves
                    for move in memory.stmemory:
                        if move['playerTurn'] == state.playerTurn:
                            move['value'] = 1 if winner == state.playerTurn else -1

                    memory.commit_ltmemory()

                logger.info('%s WINS!', players[winner]['name'])
                scores[players[winner]['name']] += 1
                if winner == BEST_PLAYER_ID:
                    sp_scores['sp'] = sp_scores['sp'] + 1
                else:
                    sp_scores['nsp'] = sp_scores['nsp'] + 1

                pts = state.score
                for i in range(len(pts)):
                    points[players[i]['name']].append(pts[i])

    return (scores, memory, points, sp_scores)
