from sets import Set
from random import randint
from terminal_colors import *

class Player:
  def __init__(self, identifier):
    self.identifier = identifier
    self.pieces = []
    self.connection = None
    self.score = 0
    self.waitingForAck = True
    self.state = True
    self.lastPackageSent = None

  def getPieceByIdx(self, idx):
    if len(self.pieces)-1 >= idx and idx >= 0:
      return self.pieces[idx]
    else:
      return False

  def __eq__(self, other):
    if(other == None):
      return False
    return self.identifier == other.identifier

  def setConnection(self, connection):
    self.connection = connection

  def hasConnection(self):
    return not(self.connection == None)

  def getBiggestPiece(self):
    biggest = self.pieces[0]
    for p in self.pieces:
      if (p[0] + p[1]) > biggest[0] + biggest[1]:
        biggest = p
    return biggest

  def discardPiece(self, piece):
    self.pieces.remove(piece)
    return piece

  def receivePiece(self, piece):
    self.pieces.append(piece)

  def piecesOptions(self):
    piecesOptions = ""
    i = 0
    for p in self.pieces:
      piecesOptions = piecesOptions + "p{i}: [{head}, {tail}]\n".format(i=i, head=p[0], tail=p[1])
      i = i + 1
    return piecesOptions

  def printPiece(self, index):
    piece = ""
    p = self.pieces[index]
    piece = "[{head}, {tail}]".format(head=p[0], tail=p[1])
    return piece

  def resetHand(self):
    self.pieces = []


class DomiLepo:
  def __init__(self, size):
    print size
    self.players = [
     Player('Blue'),
     Player('Red'),
    ]
    if(size == 4):
      self.players = [
       Player('Blue'),
       Player('Yellow'),
       Player('Red'),
       Player('Green')
      ]
    self.teams = 2
    self.maxScore = 7

    self.currentTurn = self.players[0]
    self.gameOver = True
    self.skipCount = 0
    self.lastPiecePoints = 0
    self.newGame()

  def setPieces(self):
    self.pieces = [
      [6, 6],
      [6, 5],
      [6, 4],
      [6, 3],
      [6, 2],
      [6, 1],
      [6, 0],

      [5, 5],
      [5, 4],
      [5, 3],
      [5, 2],
      [5, 1],
      [5, 0],

      [4, 4],
      [4, 3],
      [4, 2],
      [4, 1],
      [4, 0],

      [3, 3],
      [3, 2],
      [3, 1],
      [3, 0],

      [2, 2],
      [2, 1],
      [2, 0],

      [1, 1],
      [1, 0],

      [0, 0],
    ]

  def getPlayerbySocket(self, connection):
    for p in self.players:
      if p.connection == connection:
        return p
    return None

  def playPiece(self, piece, position):
    self.skipCount = 0
    self.currentTurn.discardPiece(piece)
    colorsPrintMethod = getattr(Colors, self.currentTurn.identifier.lower())
    self.usedPieces.append([piece, colorsPrintMethod(self.currentTurn.identifier)])
    # print "[{a},{s}]".format(a=piece[0], s = piece[1])
    if(piece[0] == piece[1]):
      if(self.heads[0] == self.heads[1]):
        self.lastPiecePoints=4
      else:
        self.lastPiecePoints=2
    elif((self.heads[0] == piece[0] and self.heads[1] == piece[1]) or (self.heads[1] == piece[0] and  self.heads[0] == piece[1])):
      self.lastPiecePoints=3
    else:
      self.lastPiecePoints=1
    if len(self.currentTurn.pieces) == 0:
        self.endGame()
    else:
      if self.heads[position] == piece[0]:
        self.heads[position] = piece[1]
      else:
        self.heads[position] = piece[0]
      self.setNextTurn()

  def endGame(self):
    self.gameOver = True
    if(self.skipCount == 3):
      tempScore = [0,0]
      for i in range(len(self.players)):
        tempScore[i%2] += self.players[i].score
      if(tempScore[0] > tempScore [1]):
        self.currentTurn = self.players[1]
      elif(tempScore[0] < tempScore [1]):
        self.currentTurn = self.players[0]
      else:
        self.currentTurn = None
        return
    self.currentTurn.score += self.lastPiecePoints

  def canUsePiece(self, piece):
    positions = Set([])
    if self.heads[0] == self.heads[1]:
      if self.heads[0] == piece[0]:
        positions.add(0)
      if self.heads[0] == piece[1]:
        positions.add(0)
    else:
      if piece[0] == self.heads[0]:
        positions.add(0)
      if piece[0] == self.heads[1]:
        positions.add(1)

      if piece[1] == self.heads[0]:
        positions.add(0)

      if piece[1] == self.heads[1]:
        positions.add(1)

    return positions

  def readyToStart(self):
    return len(self.pendingConnectionPlayers()) == 0

  def connectPlayer(self, connection):
    player = None
    if (len(self.pendingConnectionPlayers()) > 0):
      player = self.pendingConnectionPlayers()[0]
      player.setConnection(connection)

    return player

  def pendingConnectionPlayers(self):
    pendingPlayers = []
    for p in self.players:
      if not p.hasConnection():
          pendingPlayers.append(p)
    return pendingPlayers

  def connectedPlayers(self):
    connectedPlayers = []
    for p in self.players:
      if (p.hasConnection()):
        connectedPlayers.append(p)
    return connectedPlayers

  def setInitialHeads(self):
    player = self.players[0]
    biggestPiece = player.getBiggestPiece()
    for p in self.players:
      playerBiggestPiece = p.getBiggestPiece()
      if ((playerBiggestPiece[0] + playerBiggestPiece[1]) > (biggestPiece[0] + biggestPiece[1])):
        player = p
        biggestPiece = playerBiggestPiece

    player.discardPiece(biggestPiece)
    self.heads = [biggestPiece[0],biggestPiece[1]]
    self.currentTurn = player
    self.usedPieces.append([biggestPiece, player.identifier])
    # print "[{a},{s}]".format(a=biggestPiece[0], s = biggestPiece[1])
    self.setNextTurn()

  def setNextTurn(self):
    if(self.skipCount == len(self.players)+1):
      self.skipCount = 0
      self.endGame()
      return False
    for idx, p in enumerate(self.players):
      if p == self.currentTurn:
        if idx == len(self.players) - 1:
          self.currentTurn = self.players[0]
          return True
        else:
          self.currentTurn = self.players[idx + 1]
          return True

  def giveCards(self):
    currentPlayer = 0;
    while (len(self.pieces) > 4):
      self.players[currentPlayer].receivePiece(self.getPiece())
      currentPlayer += 1
      if currentPlayer == len(self.players):
        currentPlayer = 0


  def getPiece(self):
    index = randint(0, len(self.pieces) - 1)
    piece = self.pieces[index]
    self.pieces.remove(piece)
    return piece

  def canDraw(self):
    if len(self.pieces) > 0:
      return True
    return False

  def drawPiece(self):
    if len(self.pieces) > 0:
      self.currentTurn.receivePiece(self.getPiece())

  def printGamePieces(self):
    gameUsedPieces = ""
    for p in self.usedPieces:
      gameUsedPieces = gameUsedPieces + "[{head}, {tail}]\n".format(head=p[0], tail=p[1])
    return gameUsedPieces

  def newGame(self):
    self.usedPieces = []
    self.heads = []
    self.setPieces()
    for p in self.players:
      p.resetHand()
    self.giveCards()
    self.setInitialHeads()
    self.gameOver = False

  def getScore(self):
    team = []
    for j in range(1, self.teams+1):
      team.append(Score(j))
    for i in range(len(self.players)):
      for t in team:
        if t.id == i%self.teams + 1:
          t.players.append(self.players[i])
          t.score += self.players[i].score
    return team

class Score:
    def __init__(self, id):
      self.id = id
      self.players = []
      self.score = 0
