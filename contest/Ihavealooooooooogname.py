# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint
from game import Directions, Actions


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='OffensiveReflexAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)
        # actions.remove(Directions.STOP)
        score = -float("inf")
        alpha = -float("inf")
        beta = float("inf")
        nextaction = Directions.STOP
        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            offencer = [a for a in enemies if not a.isPacman and a.getPosition() != None]
            if len(offencer) is not 0:
                if gameState.getAgentState(self.index).scaredTimer is not 0:
                    break
                flag = 0
                for o in offencer:
                    x, y = gameState.getAgentState(self.index).getPosition()
                    if self.getMazeDistance((x, y), o.getPosition()) > 5:
                        flag += 1
                if flag == len(offencer):
                    break
                nextState = self.getSuccessor(gameState, action)
                prevscore = score
                score = max(score, alphabeta(self, nextState, 4, 'min', alpha, beta, successor, 1))
                if score > prevscore:
                    nextaction = action
            else:
                break
            alpha = max(alpha, score)
        values = [self.evaluate(gameState, a) for a in actions]
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
        if alpha > -9999:
            return nextaction
        else:
            maxValue = max(values)
            bestActions = [a for a, v in zip(actions, values) if v == maxValue]

            return random.choice(bestActions)

            # bestActions = [a for a, v in zip(actions, alpha) if v == maxValue]

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}


def alphabeta(self, gameState, depth, method, alpha, beta, successor, num):
    if depth is 0:
        return self.evaluate(gameState, Directions.STOP)
    ghost_num = 2
    # walls = gameState.getWalls()

    if method is 'max':
        value = -float("inf")
        actions = gameState.getLegalActions(self.index)
        actions.remove(Directions.STOP)
        for action in actions:
            nextstate = gameState.generateSuccessor(self.index, action)
            alpha = max(alpha, alphabeta(self, nextstate, depth - 1, 'min', alpha, beta, successor, 1))
            if alpha >= beta:
                return beta
        return alpha
    else:
        value = float("inf")
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        e = [i for i in self.getOpponents(successor)]

        index = [i for i in range(len(enemies)) if not enemies[i].isPacman and enemies[i].getPosition() != None]
        defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        # index = [i for i in self.getOpponents(successor)]
        # print(index)
        if self.red is True:
            if index[num - 1] == 0:
                g_index = 1
            else:
                g_index = 3
        else:
            if index[num - 1] == 0:
                g_index = 0
            else:
                g_index = 2
        # print(g_index)



        actions = gameState.getLegalActions(g_index)
        if num == len(index):
            for action in actions:
                value = min(value,
                            alphabeta(self, gameState.generateSuccessor(g_index, action), depth - 1, 'max', alpha, beta,
                                      successor, num))
                if alpha >= value:
                    return value
                beta = min(beta, value)
        else:
            for action in actions:
                value = min(value,
                            alphabeta(self, gameState.generateSuccessor(g_index, action), depth, 'min', alpha, beta,
                                      successor, 2))
                if alpha >= value:
                    return value
                beta = min(beta, value)
        return value


def myevaluate(currentGameState):
    maxv = 9999
    foodscore = 0
    closestfood = maxv
    closestghost = maxv
    ghostscore = 0
    scardghost = maxv
    scaredscore = 0
    closestcapsule = maxv
    capsulescore = 0
    if currentGameState.isWin():
        return maxv
    if currentGameState.isLose():
        return -maxv
    currentPos = currentGameState.getPacmanPosition()
    currentFood = currentGameState.getFood()
    GhostStates = currentGameState.getGhostStates()
    alldis = 0
    allcap = 0
    # foodsocre
    foodlist = currentFood.asList()
    capsules = currentGameState.getCapsules()
    capsulnum = len(capsules)
    for food in foodlist:
        dis = util.manhattanDistance(currentPos, food)
        alldis += dis
        closestfood = min(closestfood, dis)
    foodscore = closestfood
    foodnum = len(foodlist)

    # ghostscore
    for ghoststate in GhostStates:
        ghostpos = ghoststate.getPosition()
        # print(ghostpos)
        scared = ghoststate.scaredTimer
        if scared:
            scardghost = min(scardghost, util.manhattanDistance(currentPos, ghostpos))
        else:
            closestghost = min(closestghost, util.manhattanDistance(currentPos, ghostpos))
    if capsules:
        for capsule in capsules:
            dis = util.manhattanDistance(currentPos, capsule)
            allcap += dis
            closestcapsule = min(closestcapsule, dis)
    else:
        closestcapsule = 0

    scaredscore = scardghost if scardghost is not maxv else 0
    ghostscore = - min(closestghost, 3)
    score = currentGameState.getScore()
    # score = score - closestfood - 30*closestcapsule - scaredscore - 0.5*alldis if closestfood < closestghost and closestghost < 2 else score
    # score = score*3 if closestfood<closestghost + 1 else score
    score = score if closestfood < closestghost + 1 else score
    score -= 0.35 * alldis
    score -= 3 * scaredscore
    score -= 3 * closestcapsule
    # score = 10000.0/closestcapsule - 1.0/ghostscore - foodnum
    return score


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """

    def __init__(self, index):
        self.index = index
        self.observationHistory = []

    def getFeatures(self, gameState, action):
        # Start like getFeatures of OffensiveReflexAgent
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        food = self.getFood(gameState)
        capsules = gameState.getCapsules()
        foodList = food.asList()
        walls = gameState.getWalls()
        x, y = gameState.getAgentState(self.index).getPosition()
        vx, vy = Actions.directionToVector(action)
        newx = int(x + vx)
        newy = int(y + vy)

        enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
        invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        defenders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        if not successor.getAgentState(self.index).isPacman:
            features['ispacman'] = -1
        else:
            features['ispacman'] = 1

        if action == Directions.STOP:
            features["stuck"] = 1.0

        # Get ghosts close by
        features['normalGhosts'] = 0
        features["scaredGhosts"] = 0
        features['scared'] = 0
        for ghost in invaders:
            ghostpos = ghost.getPosition()
            neighbors = Actions.getLegalNeighbors(ghostpos, walls)
            if (newx, newy) == ghostpos:
                if ghost.scaredTimer == 0:
                    features["scaredGhosts"] = 0
                    dis = self.getMazeDistance((newx, newy), ghost.getPosition()) < 5
                    if dis < 5:
                        features['scared'] = 0.5
                        features["normalGhosts"] = -dis
                    else:
                        features['normalGhosts'] = 0
                else:
                    features["eatFood"] += 200
                    # features["eatGhost"] += 1
            elif ((newx, newy) in neighbors) and (ghost.scaredTimer > 0):
                dis = self.getMazeDistance((newx, newy), ghost.getPosition())
                if dis < 5:
                    features["scaredGhosts"] = dis
                    # features['eatGhost'] = -10000
                else:
                    features["scaredGhosts"] = 0
                    # features['eatGhost'] = 0
            elif (successor.getAgentState(self.index).isPacman) and (ghost.scaredTimer > 0):
                features["scaredGhosts"] = 0
                features["normalGhosts"] += 1


        if gameState.getAgentState(self.index).scaredTimer == 0 and not successor.getAgentState(self.index).isPacman:
            for ghost in defenders:
                ghostpos = ghost.getPosition()
                neighbors = Actions.getLegalNeighbors(ghostpos, walls)
                if (newx, newy) == ghostpos:
                    features["eatInvader"] = 1000
                elif (newx, newy) in neighbors:
                    features["closeInvader"] += 1000
        elif gameState.getAgentState(self.index).scaredTimer > 0 and not successor.getAgentState(self.index).isPacman:
            for ghost in enemies:
                if ghost.getPosition() != None:
                    ghostpos = ghost.getPosition()
                    neighbors = Actions.getLegalNeighbors(ghostpos, walls)
                    if (newx, newy) in neighbors:
                        features["closeInvader"] += -100
                        features["eatInvader"] = -100
                    elif (newx, newy) == ghostpos:
                        features["eatInvader"] = -100
        else:
            features["eatInvader"] = 0
            features["closeInvader"] = 0
        for cx, cy in capsules:
            if newx == cx and newy == cy and successor.getAgentState(self.index).isPacman:
                features["eatCapsule"] = 1.0

        if not features["normalGhosts"]:
            if food[newx][newy]:
                features["eatFood"] = 1.0
            if len(foodList) > 0:
                tempFood = []
                for food in foodList:
                    food_x, food_y = food
                    adjustedindex = self.index - self.index % 2
                    check1 = food_y > (adjustedindex / 2) * walls.height / 3
                    check2 = food_y < ((adjustedindex / 2) + 1) * walls.height / 3
                    if (check1 and check2):
                        tempFood.append(food)
                if len(tempFood) == 0:
                    tempFood = foodList
                mazedist = [self.getMazeDistance((newx, newy), food) for food in tempFood]
                if min(mazedist) is not None:
                    walldimensions = walls.width * walls.height
                    features["nearbyFood"] = float(min(mazedist)) / walldimensions
        # features.divideAll(10.0)
        # print(features)
        return features

    def getWeights(self, gameState, action):
        return {'eatInvader': 5, 'closeInvader': 1, 'teammateDist': 1.5, 'nearbyFood': -2, 'eatCapsule': 100.0,
                'normalGhosts': -20, 'scaredGhosts': -100, 'stuck': -5, 'eatFood': 10,
                'ispacman': 50, 'scared': -100, 'eatGhost': -1}


class DefensiveReflexAgent(ReflexCaptureAgent):
    def __init__(self, index):
        self.index = index
        self.observationHistory = []

        # Follows from getSuccessor function of ReflexCaptureAgent

    def getFeatures(self, gameState, action):
        # Start like getFeatures of OffensiveReflexAgent
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        # Get other variables for later use
        food = self.getFood(gameState)
        capsules = gameState.getCapsules()
        foodList = food.asList()
        walls = gameState.getWalls()
        x, y = gameState.getAgentState(self.index).getPosition()
        vx, vy = Actions.directionToVector(action)
        newx = int(x + vx)
        newy = int(y + vy)

        # Get set of invaders and defenders
        enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
        invaders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        defenders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        # Check if pacman has stopped
        if action == Directions.STOP:
            features["stuck"] = 1.0

        # Get ghosts close by
        for ghost in invaders:
            ghostpos = ghost.getPosition()
            neighbors = Actions.getLegalNeighbors(ghostpos, walls)
            if (newx, newy) == ghostpos:
                if ghost.scaredTimer == 0:
                    features["scaredGhosts"] = 0
                    features["normalGhosts"] = 1
                else:
                    features["eatFood"] += 2
                    features["eatGhost"] += 10
            elif ((newx, newy) in neighbors) and (ghost.scaredTimer > 0):
                features["scaredGhosts"] += 1
            elif (successor.getAgentState(self.index).isPacman) and (ghost.scaredTimer > 0):
                features["scaredGhosts"] = 0
                features["normalGhosts"] += 1

        # How to act if scared or not scared
        if gameState.getAgentState(self.index).scaredTimer == 0:
            for ghost in defenders:
                ghostpos = ghost.getPosition()
                neighbors = Actions.getLegalNeighbors(ghostpos, walls)
                if (newx, newy) == ghostpos:
                    features["eatInvader"] = 10
                elif (newx, newy) in neighbors:
                    features["closeInvader"] += 10
        else:
            for ghost in enemies:
                if ghost.getPosition() != None:
                    ghostpos = ghost.getPosition()
                    neighbors = Actions.getLegalNeighbors(ghostpos, walls)
                    if (newx, newy) in neighbors:
                        features["closeInvader"] += -10
                        features["eatInvader"] = -10
                    elif (newx, newy) == ghostpos:
                        features["eatInvader"] = -10

        # Get capsules when nearby
        for cx, cy in capsules:
            if newx == cx and newy == cy and successor.getAgentState(self.index).isPacman:
                features["eatCapsule"] = 1.0

        # When to eat
        if not features["normalGhosts"]:
            if food[newx][newy]:
                features["eatFood"] = 1.0
            if len(foodList) > 0:
                tempFood = []
                for food in foodList:
                    food_x, food_y = food
                    adjustedindex = self.index - self.index % 2
                    check1 = food_y > (adjustedindex / 2) * walls.height / 3
                    check2 = food_y < ((adjustedindex / 2) + 1) * walls.height / 3
                    if (check1 and check2):
                        tempFood.append(food)
                if len(tempFood) == 0:
                    tempFood = foodList
                mazedist = [self.getMazeDistance((newx, newy), food) for food in tempFood]
                if min(mazedist) is not None:
                    walldimensions = walls.width * walls.height
                    features["nearbyFood"] = float(min(mazedist)) / walldimensions
        features.divideAll(10.0)
        return features

    def getWeights(self, gameState, action):
        return {'eatInvader': 5, 'closeInvader': 0, 'teammateDist': 1.5, 'nearbyFood': -10, 'eatCapsule': 100.0,
                'normalGhosts': -200, 'eatGhost': 10.0, 'scaredGhosts': -100, 'stuck': -50, 'eatFood': 10}
