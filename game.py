from sets import Set
from random import randint

class Player:
  def __init__(self, identifier):
    self.identifier = identifier
    self.pieces = []
    self.connection = None

  def getPieceByIdx(self, idx):
    if len(self.pieces) >= idx and idx > 0:
      return self.pieces[idx]
    else:
      return False

  def __eq__(self, other):
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

  def receivePiece(self, piece):
    self.pieces.append(piece)

  def piecesOptions(self):
    piecesOptions = ""
    i = 0
    for p in self.pieces:
      piecesOptions = piecesOptions + "p{i}: [{head}, {tail}]\n".format(i=i, head=p[0], tail=p[1])
      i = i + 1
    return piecesOptions

class DomiLepo:
  def __init__(self):
    self.players = [
      Player('blue'),
      Player('yellow')
      # Player('red'),
      # Player('green')
    ]

    self.currentTurn = self.players[0]

    self.heads = []
    self.usedPieces = []
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

    self.giveCards()
    self.setInitialHeads()

  def getPlayerbySocket(self, connection):
    for p in self.players:
      if p.connection == connection:
        return p
    return None

  def playPiece(self, piece, position):
    self.currentTurn.discardPiece(piece)
    if self.heads[position] == piece[0]:
      self.heads[position] = piece[1]
    else:
      self.heads[position] = piece[0]
    self.setNextTurn()

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
    if(len(self.pendingConnectionPlayers()) > 0):
      self.pendingConnectionPlayers()[0].setConnection(connection)

  def pendingConnectionPlayers(self):
    pendingPlayers = []
    for p in self.players:
      if not p.hasConnection():
        pendingPlayers.append(p)
    return pendingPlayers

  def connectedPlayers(self):
    connectedPlayers = []
    for p in self.players:
      if(p.hasConnection()):
        connectedPlayers.append(p)
    return connectedPlayers

  def setInitialHeads(self):
    player = self.players[0]
    biggestPiece = player.getBiggestPiece()
    for p in self.players:
      playerBiggestPiece = p.getBiggestPiece()
      if((playerBiggestPiece[0] + playerBiggestPiece[1]) > (biggestPiece[0] + biggestPiece[1])):
        player = p
        biggestPiece = playerBiggestPiece

    player.discardPiece(biggestPiece)
    self.heads = biggestPiece
    self.currentTurn = player

    self.usedPieces.append([biggestPiece, player])

  def setNextTurn(self):
    for idx, p in enumerate(self.players):
      if p == self.currentTurn:
        if idx == len(self.players) - 1:
          self.currentTurn = self.players[0]
          return
        else:
          self.currentTurn = self.players[idx + 1]
          return

  def giveCards(self):
    currentPlayer = 0;
    while(len(self.pieces) > 4):
      self.players[currentPlayer].receivePiece(self.getPiece())
      currentPlayer+=1
      if currentPlayer == len(self.players):
        currentPlayer = 0

  def getPiece(self):
    index = randint(0, len(self.pieces) - 1)
    piece = self.pieces[index]
    self.pieces.remove(piece)
    return piece

  def printGamePieces(self):
    gameUsedPieces = ""
    i = 0
    for p in self.pieces:
      gameUsedPieces = gameUsedPieces + "[{head}, {tail}]\n".format(head=p[0], tail=p[1])
      i = i + 1
    return gameUsedPieces
