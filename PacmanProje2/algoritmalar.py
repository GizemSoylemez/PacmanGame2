# multiAgents.py
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


class ReflexAgent(Agent):


    def getAction(self, gameState):


        legalMoves = gameState.getLegalActions()

        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):

        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]


        heuristic = 0
        for states in newScaredTimes:
            heuristic += states
        for ghost in newGhostStates:
            ghostDist += [manhattanDistance(ghost.getPosition(), newPos)]
            if ghost.getDirection() == Directions.STOP:
                heuristic -= 20
        minGhost = min(ghostDist)
        foodList = newFood.asList()
        foodDist = []
        for food in foodList:
            foodDist += [manhattanDistance(food, newPos)]
        if currentGameState.getNumFood() > successorGameState.getNumFood():
            heuristic += 100
        inverse = 0
        if len(foodDist) > 0:
            inverse = (1.0 / float(min(foodDist)))
        if minGhost < 5:
            minGhost = minGhost * 0.5
        if minGhost >= 5 and minGhost <= 20:
            minGhost = minGhost * 1.1
        if minGhost > 20:
            minGhost = minGhost * 1.7
        heuristic += minGhost + successorGameState.getScore() + inverse * 100
        return heuristic


def scoreEvaluationFunction(currentGameState):

    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      Bu sınıf, tüm üyelerinize ortak öğeler sağlar.
       çok ajanlı arama yapanlar. Burada tanımlanan herhangi bir yöntem mevcut olacak
       MinimaxPacmanAgent, AlphaBetaPacmanAgent ve ExpectimaxPacmanAgent için.

       Burada * herhangi bir değişiklik yapmanız gerekmez, ancak isterseniz
       tüm rakip arama ajanlarınıza işlevsellik ekleyin. Lütfen yapma
       ancak bir şeyleri kaldırın.

       Not: Bu soyut bir sınıftır: somutlaştırılmaması gereken. Onun
       sadece kısmen belirtilmiş ve genişletilmek üzere tasarlanmıştır. Ajan (game.py)
       başka bir soyut sınıftır.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # her zaman index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):



    def getAction(self, gameState):
        """
         Self.depth komutunu kullanarak geçerli gameState öğesinden minimax işlemini döndürür
           ve kendini değerlendirme işlevi.

           İşte minimax uygulanırken faydalı olabilecek bazı yöntem çağrıları.

           gameState.getLegalActions (agentIndex):
             Bir aracı için yasal işlemlerin bir listesini döndürür
             agentIndex = 0, Pacman anlamına gelir, hayaletler> = 1

           gameState.generateSuccessor (agentIndex, action):
             Bir aracı işlem yaptıktan sonra halefi oyun durumunu döndürür

           gameState.getNumAgents ():
             Oyundaki toplam oyuncu sayısını döndürür

           gameState.isWin ():
             Oyun durumunun kazanan bir durum olup olmadığını döndürür

           gameState.isLose ():
             Oyun durumunun kaybedilen bir durum olup olmadığını döndürür
        """
        result = self.value(gameState, 0)
        return result[1]

    def value(self, gameState, depth):
        numAgents = gameState.getNumAgents()
        if gameState.isWin() or gameState.isLose() or (depth == self.depth * numAgents):
            return (self.evaluationFunction(gameState), None)

        if ((depth % numAgents) == 0):  # max
            return self.minOrMax(gameState, depth, 1)
        else:  # min
            return self.minOrMax(gameState, depth, 0)

    def minOrMax(self, gameState, depth, pacman):
        agent = [depth % gameState.getNumAgents(), 0]
        values = [float("inf"), float("-inf")]
        val = (values[pacman], None)
        possibleActions = gameState.getLegalActions(agent[pacman])
        if len(possibleActions) == 0:
            return (self.evaluationFunction(gameState), None)
        for action in possibleActions:
            successor = gameState.generateSuccessor(agent[pacman], action)
            result = self.value(successor, depth + 1)
            if ((pacman == 1) and result[0] > val[0]) or ((pacman == 0) and (result[0] < val[0])):
                val = (result[0], action)
        return val


class AlphaBetaAgent(MultiAgentSearchAgent):
     """
           Alfa beta budama özelliğine sahip minimax
         """

    def getAction(self, gameState):
        """
           Self.depth ve self.evaluationFunction işlevini kullanarak minimax eylemini döndürür
         """

        # alfa negatif olarak başlar (maksimize eder), beta pozitif başlar (minimize eder)
        result = self.value(gameState, 0, -float("inf"), float("inf"))
        return result[1]

    def value(self, gameState, depth, alpha, beta):
        numAgents = gameState.getNumAgents()
        if gameState.isWin() or gameState.isLose() or (depth == self.depth * numAgents):
            return (self.evaluationFunction(gameState), None)

        if ((depth % numAgents) == 0):
            return self.minOrMax(gameState, depth, 1, alpha, beta)
        else:
            return self.minOrMax(gameState, depth, 0, alpha, beta)

    def minOrMax(self, gameState, depth, pacman, alpha, beta):
        agent = [depth % gameState.getNumAgents(), 0]
        values = [float("inf"), float("-inf")]
        val = (values[pacman], None)
        possibleActions = gameState.getLegalActions(agent[pacman])
        if len(possibleActions) == 0:
            return (self.evaluationFunction(gameState), None)
        for action in possibleActions:
            successor = gameState.generateSuccessor(agent[pacman], action)
            result = self.value(successor, depth + 1, alpha, beta)
            if pacman:
                if result[0] > val[0]:
                    val = (result[0], action)
                if val[0] > beta:
                    return val
                alpha = max(alpha, val[0])
            else:
                if result[0] < val[0]:
                    val = (result[0], action)
                if val[0] < alpha:
                    return val
                beta = min(beta, val[0])
        return val


class ExpectimaxAgent(MultiAgentSearchAgent):


    def getAction(self, gameState):
        """
      Self.depth ve self.evaluationFunction işlevini kullanarak expectimax eylemini döndürür
           Tüm hayaletler rastgele seçtikleri seçimlerden modellenmelidir.
           yasal hamle.
        """
        result = self.value(gameState, 0)
        return result[1]

    def value(self, gameState, depth):
        numAgents = gameState.getNumAgents()
        if gameState.isWin() or gameState.isLose() or (depth == self.depth * numAgents):
            return (self.evaluationFunction(gameState), None)

        if ((depth % numAgents) == 0):  # sonraki hayalet max
            return self.expectOrMax(gameState, depth, 1)
        else:  # sonraki hayalet min
            return self.expectOrMax(gameState, depth, 0)

    def expectOrMax(self, gameState, depth, pacman):
        agent = [depth % gameState.getNumAgents(), 0]
        values = [0, float("-inf")]
        val = (values[pacman], None)
        possibleActions = gameState.getLegalActions(agent[pacman])
        if len(possibleActions) == 0:
            return (self.evaluationFunction(gameState), None)
        for action in possibleActions:
            successor = gameState.generateSuccessor(agent[pacman], action)
            result = self.value(successor, depth + 1)
            if pacman:
                if result[0] > val[0]:
                    val = (result[0], action)
            else:
                p = 1.0 / float(len(possibleActions))
                val = (val[0] + (result[0] * p), action)
        return val


def betterEvaluationFunction(currentGameState):

    successorGameState = currentGameState
    newPos = successorGameState.getPacmanPosition()
    newFood = successorGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    heuristic = 0
    for states in newScaredTimes:
        heuristic += states
    ghostDist = []
    for ghost in newGhostStates:
        ghostDist += [manhattanDistance(ghost.getPosition(), newPos)]
        if ghost.getDirection() == Directions.STOP:
            heuristic -= 20
    minGhost = min(ghostDist)
    foodList = newFood.asList()
    foodDist = []
    for food in foodList:
        foodDist += [manhattanDistance(food, newPos)]
    if currentGameState.getNumFood() > successorGameState.getNumFood():
        heuristic += 100
    inverse = 0
    if len(foodDist) > 0:
        inverse = (1.0 / float(min(foodDist)))
    if minGhost < 5:
        minGhost = minGhost * 0.5
    if minGhost >= 5 and minGhost <= 20:
        minGhost = minGhost * 1.1
    if minGhost > 20:
        minGhost = minGhost * 1.7
    heuristic += minGhost + successorGameState.getScore() + inverse * 100
    return heuristic

better = betterEvaluationFunction

