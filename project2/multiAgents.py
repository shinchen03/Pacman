# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        if successorGameState.isWin():
            return 999999
        ghostpos = currentGameState.getGhostPosition(1)
        distfromghost = util.manhattanDistance(ghostpos, newPos)
        score = successorGameState.getScore()
        nextfood = 999999
        foodlist = newFood.asList()
        for food in foodlist:
            dist = util.manhattanDistance(food, newPos)
            if dist < nextfood:
                nextfood = dist
        if (currentGameState.getNumFood() > successorGameState.getNumFood()):
            score += 100
        if action == Directions.STOP:
            score -= 5
        score -= 5 * nextfood
        capsuleplaces = currentGameState.getCapsules()
        if successorGameState.getPacmanPosition() in capsuleplaces:
            score += 120
        return score


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          Directions.STOP:
            The stop direction, which is always legal

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        legalActions = gameState.getLegalActions()
        numghosts = gameState.getNumAgents() - 1
        nextaction = Directions.STOP
        score = -999999
        for action in legalActions:
            nextState = gameState.generateSuccessor(0, action)
            prevscore = score
            score = max(score, min_max(self, nextState, self.depth, 'min', 1))
            if score > prevscore:
                nextaction = action
        return nextaction


def min_max(self, gameState, depth, method, num=None):
    if depth is 0 or gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)
    ghost_num = gameState.getNumAgents() - 1
    if method is 'max':
        actions = gameState.getLegalActions(0)
        maxvalue = -999999
        for action in actions:
            nextstate = gameState.generateSuccessor(0, action)
            score = min_max(self, nextstate, depth - 1, 'min', 1)
            if score > maxvalue:
                maxvalue = score
        return maxvalue
    else:
        minvalue = +999999
        actions = gameState.getLegalActions(num)
        if num == ghost_num:
            for action in actions:
                score = min_max(self, gameState.generateSuccessor(num, action), depth - 1, 'max')
                if score < minvalue:
                    minvalue = score
        else:
            for action in actions:
                score = min_max(self, gameState.generateSuccessor(num, action), depth, 'min', num+1)
                if score < minvalue:
                    minvalue = score
        return minvalue


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        legalActions = gameState.getLegalActions()
        numghosts = gameState.getNumAgents() - 1
        nextaction = Directions.STOP
        score = -999999
        alpha = -999999
        beta = 999999
        for action in legalActions:
            nextState = gameState.generateSuccessor(0, action)
            prevscore = score
            score = max(score, alphabeta(self, nextState, self.depth, 'min', alpha, beta, numghosts))
            if score > prevscore:
                nextaction = action

            alpha = max(alpha, score)
        return nextaction

def alphabeta(self, gameState, depth, method, alpha, beta, num=None):
    if depth is 0 or gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)
    ghost_num = gameState.getNumAgents() - 1
    if method is 'max':
        value = -999999
        actions = gameState.getLegalActions(0)
        actions.remove(Directions.STOP)
        for action in actions:
            nextstate = gameState.generateSuccessor(0, action)
            alpha = max(alpha, alphabeta(self, nextstate, depth - 1, 'min', alpha, beta, 1))
            if alpha >= beta:
                return beta
        return alpha
    else:
        value = 999999
        actions = gameState.getLegalActions(num)
        if num == ghost_num:
            for action in actions:
                value = min(value, alphabeta(self, gameState.generateSuccessor(num, action), depth - 1, 'max', alpha, beta))
                if alpha >= value:
                    return value
                beta = min(beta, value)
        else:
            for action in actions:
                value = min(value, alphabeta(self, gameState.generateSuccessor(num, action), depth, 'min', alpha, beta, num + 1))
                if alpha >= value:
                    return value
                beta = min(beta, value)
        return value


class ExpectimaxAgent(MultiAgentSearchAgent):

    def getAction(self, gameState):
        legalActions = gameState.getLegalActions()
        numghosts = gameState.getNumAgents() - 1
        nextaction = Directions.STOP
        score = -999999
        test = {}
        bestmoves = []
        legalActions.remove(Directions.STOP)
        for action in legalActions:
            nextState = gameState.generateSuccessor(0, action)
            prevscore = score
            currentscore = max_exp(self, nextState, self.depth, 'exp', 1)
            test.update({action: currentscore})
            score = max(score, currentscore)
            if score > prevscore:
                nextaction = action
        #print(test)
        for key in test:
            if test[key] == score:
                bestmoves.append(key)
        return nextaction


def max_exp(self, gameState, depth, method, num=None):
    if depth is 0 or gameState.isWin() or gameState.isLose():
        return self.evaluationFunction(gameState)
    ghost_num = gameState.getNumAgents() - 1
    if method is 'max':
        actions = gameState.getLegalActions(0)
        maxvalue = -999999
        for action in actions:
            nextstate = gameState.generateSuccessor(0, action)
            score = max_exp(self, nextstate, depth - 1, 'exp', 1)
            if score > maxvalue:
                maxvalue = score
        return maxvalue
    else:
        v = 0
        actions = gameState.getLegalActions(num)
        p = 1.0 / (len(actions))
        for action in actions:
            if num is ghost_num:
                v += max_exp(self, gameState.generateSuccessor(num, action), depth-1, 'max')
            else:
                v += max_exp(self, gameState.generateSuccessor(num, action), depth, 'exp', num+1)
        return v*p


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
      if ghost is not close to the pacman, score*2
      minus the sum of distance from all foods
      in order to dismiss the situation that pacman don't know where to go
      due to the same score states
    """
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
    #foodsocre
    foodlist = currentFood.asList()
    capsules = currentGameState.getCapsules()
    capsulnum = len(capsules)
    for food in foodlist:
        dis = util.manhattanDistance(currentPos,food)
        alldis += dis
        closestfood = min(closestfood, dis)
    foodscore = closestfood
    foodnum = len(foodlist)

    #ghostscore
    for ghoststate in GhostStates:
        ghostpos = ghoststate.getPosition()
        #print(ghostpos)
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
    #score = score - closestfood - 30*closestcapsule - scaredscore - 0.5*alldis if closestfood < closestghost and closestghost < 2 else score
    #score = score*3 if closestfood<closestghost + 1 else score
    score = score if closestfood<closestghost + 1 else score
    score = score - 100*capsulnum if not scared else score
    score -= 0.35*alldis
    score -= 3*scaredscore
    score -= 3*closestcapsule
    #score = 10000.0/closestcapsule - 1.0/ghostscore - foodnum
    return score

# Abbreviation
better = betterEvaluationFunction


class ContestAgent(MultiAgentSearchAgent):
    """
      Your agent for the mini-contest
    """


    def getAction(self, gameState):

        legalActions = gameState.getLegalActions()
        numghosts = gameState.getNumAgents() - 1
        nextaction = Directions.STOP
        score = -999999
        alpha = -999999
        beta = 999999
        ########################
        #legalActions.remove(Directions.STOP)
        for action in legalActions:
            nextState = gameState.generateSuccessor(0, action)
            prevscore = score
            score = max(score, alphabeta_con(self, nextState, 9, 'min', alpha, beta, 1))
            if score > prevscore:
                nextaction = action

            alpha = max(alpha, score)
        return nextaction


def alphabeta_con(self, gameState, depth, method, alpha, beta, num=None):
    if depth is 0 or gameState.isWin() or gameState.isLose():
        return evaluation_con(gameState)
    ghost_num = gameState.getNumAgents() - 1
    if method is 'max':
        value = -999999
        actions = gameState.getLegalActions(0)
        actions.remove(Directions.STOP)
        for action in actions:
            nextstate = gameState.generateSuccessor(0, action)
            alpha = max(alpha, alphabeta_con(self, nextstate, depth - 1, 'min', alpha, beta, 1))
            if alpha >= beta:
                return beta
        return alpha
    else:
        value = 999999
        actions = gameState.getLegalActions(num)
        if num == ghost_num:
            for action in actions:
                value = min(value, alphabeta_con(self, gameState.generateSuccessor(num, action), depth - 1, 'max', alpha, beta))
                if alpha >= value:
                    return value
                beta = min(beta, value)
        else:
            for action in actions:
                value = min(value, alphabeta_con(self, gameState.generateSuccessor(num, action), depth, 'min', alpha, beta, num + 1))
                if alpha >= value:
                    return value
                beta = min(beta, value)
        return value

def evaluation_con(currentGameState):
    maxv = 99999
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
    scarednum = 0
    #foodsocre
    foodlist = currentFood.asList()
    capsules = currentGameState.getCapsules()
    capsulnum = len(capsules)
    for food in foodlist:
        dis = util.manhattanDistance(currentPos,food)
        alldis += dis
        closestfood = min(closestfood, dis)
    foodscore = closestfood
    foodnum = len(foodlist)
    scareddis = 0
    #ghostscore
    for ghoststate in GhostStates:
        ghostpos = ghoststate.getPosition()
        #print(ghostpos)
        scared = ghoststate.scaredTimer
        if scared:
            scareddis = util.manhattanDistance(currentPos, ghostpos)
            scarednum += 1
            scardghost = min(scardghost, scareddis)
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
    #score = score - closestfood - 30*closestcapsule - scaredscore - 0.5*alldis if closestfood < closestghost and closestghost < 2 else score
    score = score*3 if closestfood<closestghost + 1 else score
    score = score - 300*capsulnum if not scarednum else score + 300*capsulnum
    score -= 0.35 * alldis
    score -= 3*foodnum
    score -= 0.6 * scaredscore
    score -= 30*scarednum
    score -= scareddis
    #score = score - 200*scarednum - scareddis if scarednum else score - 2*foodnum -0.35 * alldis
    score -= closestfood
    #score = 3*score - 5*closestcapsule if closestcapsule<closestghost + 2 else score
    #score = 10000.0/closestcapsule - 1.0/ghostscore - foodnum
    return score
#score -= 5 * scaredscore
#score -= 10*scarednum
#    score = score*3 if closestfood<closestghost + 1 else score/2
#    score = score - 100*capsulnum if not scared else score + 600*capsulnum

