# valueIterationAgents.py
# -----------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import mdp, util

from learningAgents import ValueEstimationAgent


class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """

    def __init__(self, mdp, discount=0.9, iterations=100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter()  # A Counter is a dict with default 0
        states = mdp.getStates()
        for times in range(iterations):
            value = self.values.copy()
            for state in states:
                #v = {'north': 0, 'east': 0, 'west': 0, 'south': 0}
                v = util.Counter()
                statevalue = -99999999
                actions = mdp.getPossibleActions(state)
                for action in actions:
                    #if action is 'exit':
                    #    return None
                    for nextstate, prob in mdp.getTransitionStatesAndProbs(state, action):
                        v[action] += prob * (mdp.getReward(state, action, nextstate) + discount * value[nextstate])
                for key in v:
                    temp = v[key]
                    if temp > statevalue:
                        statevalue = temp
                if len(v) is 0:
                    statevalue = 0
                self.values[state] = statevalue
    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]

    def getQValue(self, state, action):
        """
          The q-value of the state action pair
          (after the indicated number of value iteration
          passes).  Note that value iteration does not
          necessarily create this quantity and you may have
          to derive it on the fly.
        """
        Q_value = self.values[state]
        for nextstate, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            Q_value += self.discount * prob * self.values[nextstate]
        return Q_value

    def getPolicy(self, state):
        """
          The policy is the best action in the given state
          according to the values computed by value iteration.
          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        actions = self.mdp.getPossibleActions(state)
        if not actions:
            return None
        value = self.values
        statevalue = -999999
        nextaction = ''
        #v = {'north': 0, 'east': 0, 'west': 0, 'south': 0}
        v = util.Counter()
        for action in actions:
            for nextstate, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                v[action] += prob * (self.mdp.getReward(state, action, nextstate) + self.discount * value[nextstate])
        for key in v:
            temp = v[key]
            if temp > statevalue:
                statevalue = temp
                nextaction = key

        return nextaction

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.getPolicy(state)
