from random import randint

class Player:
  def __init__(self, identifier):
    self.identifier = identifier
    self.pieces = []

  def getBiggestPiece(self):
    biggest = self.pieces[0]
    for p in self.pieces:
      if (p[0] + p[1]) > biggest[0] + biggest[1]:
        biggest = p
    return biggest

  def receivePiece(self, piece):
    self.pieces.append(piece)

class DomiLepo:
  def __init__(self):
    self.players = [
      Player('blue'),
      Player('yellow'),
      Player('red'),
      Player('green')
    ]

    self.heads = []
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

  def setInitialHeads(self):
    print "DomiLepo#setInitialHeads: Not yep implemented"

  def giveCards(self):
    currentPlayer = 0;
    while(len(self.pieces) > 4):
      self.players[currentPlayer].receivePiece(self.getPiece())
      currentPlayer+=1
      if currentPlayer == 4:
        currentPlayer = 0

  def getPiece(self):
    index = randint(0, len(self.pieces) - 1)
    piece = self.pieces[index]
    self.pieces.remove(piece)
    return piece
