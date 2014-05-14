from socket import *
from terminal_colors import *
import json

class UdpServer:
  def __init__(self, game):
    self.game = game
    self.s = socket(AF_INET, SOCK_DGRAM)
    self.s.bind(('127.0.0.1', 12000))

    print "Listening to 127.0.0.1:12000\n"

    while 1:
        if(self.game.readyToStart()):
            self.sendMessageToCurrentPlayer({'type': 'message', 'message': "It's your turn"})
            self.broadcastMessage({'type': 'message', 'message': "------- {} PLAYER TURN -----".format(self.game.currentTurn.identifier.upper())})
            self.askCurrentPlayerToPlay()
            self.receiveData()
        else:
            msg, address = self.s.recvfrom(2048)
            print msg
            self.game.connectPlayer(address)

            player = self.game.getPlayerbySocket(address)
            print address;
            self.sendMessageToPlayer(player, {'type': 'message', 'message': "You are the {} player".format(player.identifier.upper())})
            self.broadcastMessage({'type': 'message', 'message': "{} player connected".format(player.identifier.upper())})
            self.broadcastMessage({'type': 'message', 'message': "Waiting for {} players to connect...".format(len(self.game.pendingConnectionPlayers()))})


  def receiveData(self):
    while 1:
      data, sender = self.s.recvfrom(1024)
      if data:
        data = json.loads(data)
        if(data['type'] == 'options'):
          if(data['selected'] == '1'):
            self.showCurrentPlayerPieces()
          elif(data['selected'] == '2'):
            self.showToCurrentPlayerGamePieces()
            self.askCurrentPlayerToPlay()
          elif(data['selected'] == '3'):
            self.showToCurrentPlayerGameHeads()
            self.askCurrentPlayerToPlay()
          elif(data['selected'] == '4'):
            self.showToCurrentPlayerPlayersPieceCount()
            self.askCurrentPlayerToPlay()

        elif(data['type'] == 'position'):
          if(data['selected'] == '0' or data['selected'] == '1'):
            self.game.playPiece(piece, int(data['selected']))
            self.broadcastMessage({'type': 'message', 'message': self.game.currentTurn.identifier.upper() + " has played [{head},{tail}].\n".format(head=piece[0], tail=piece[1])})
            self.checkEndGame()
            break
          else:
            #self.sendMessageToCurrentPlayer("Invalid Option\n")        #json dava erro ao receber esta mensagem
            self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Invalid Option\n"})
            self.askCurrentPlayerToPlay()

        elif(data['type'] == 'piece'):
          pieceIdx = data['selected'].replace('p', '')
          if pieceIdx == 'b':
            break
          elif pieceIdx == 'e':
            if(self.game.canDraw()):
              self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Can't skip yet!\n"})
            else:
              self.game.setNextTurn()
            break
          elif pieceIdx == 'd':
            if(self.game.canDraw()):
              self.game.drawPiece()
              self.broadcastMessage({'type': 'message', 'message': self.game.currentTurn.identifier.upper() + " has drawn a domino.\n"})
              self.sendMessageToCurrentPlayer({'type': 'message', 'message': "You got the "+ self.game.currentTurn.printPiece(len(self.game.currentTurn.pieces)-1) + "!\n"})
            else:
              self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Can't draw any more pieces.\n"})
            break

          piece = self.game.currentTurn.getPieceByIdx(int(pieceIdx))
          if piece == False:
            #self.sendMessageToCurrentPlayer("Invalid Piece\n")         #json dava erro ao receber esta mensagem
            self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Invalid Piece\n"})
            self.askCurrentPlayerToPlay()
          else:
            possiblePiecePositions = list(self.game.canUsePiece(piece))
            if len(possiblePiecePositions) > 0:
              if len(possiblePiecePositions) == 1:
                self.game.playPiece(piece, possiblePiecePositions[0])
                self.broadcastMessage({'type': 'message', 'message': self.game.currentTurn.identifier.upper() + " has played [{head},{tail}].\n".format(head=piece[0], tail=piece[1])})
                self.checkEndGame()
                break
              else:
                self.askPlayerToChoosePosition()
            else:
              self.sendMessageToCurrentPlayer({'type': 'message', 'message': "You cannot use this piece\n"})
              self.askCurrentPlayerToPlay()



  def askPlayerToChoosePosition(self):
    self.sendMessageToCurrentPlayer({'type': 'position', 'message': 'Please choose the piece position', 'question': '(0) for {}\n(1) for {}\n'.format(self.game.heads[0], self.game.heads[1])})

  def showToCurrentPlayerPlayersPieceCount(self):
    text = ""
    for p in self.game.players:
      text  = text + "Player {0}: {1} pieces\n".format(p.identifier.upper(), len(p.pieces))
    self.sendMessageToCurrentPlayer({'type': 'message', 'message': text})

  def showToCurrentPlayerGameHeads(self):
    self.sendMessageToCurrentPlayer({'type': 'message', 'message': Colors.red("Heads:") + " {0} {1}".format(self.game.heads[0], self.game.heads[1])})

  def showToCurrentPlayerGamePieces(self):
    self.sendMessageToCurrentPlayer({'type': 'message', 'message': self.game.printGamePieces()})

  def showCurrentPlayerPieces(self):
    if self.game.canDraw():
        self.sendMessageToCurrentPlayer({'type': 'piece', 'message': self.game.currentTurn.piecesOptions(), 'question': "Please choose a piece to play:  (Press 'd' to draw one domino or 'b' to go back)\n"})
    else:
        self.sendMessageToCurrentPlayer({'type': 'piece', 'message': self.game.currentTurn.piecesOptions(), 'question': "Please choose a piece to play:  (Press 'e' to skip your turn or 'b' to go back)\n"})

  def askCurrentPlayerToPlay(self):
    self.showToCurrentPlayerGameHeads()
    self.sendMessageToCurrentPlayer({'type': 'options', 'message': self.playerOptions(), 'question': "Please choose a option:\n"})

  def playerOptions(self):
    return Colors.blue("(1)") + " Your pieces\n" + Colors.blue("(2)") + " Pieces in game\n" + Colors.blue("(3)") + " Shows heads\n" + Colors.blue("(4)") + " Show players piece count"

  def sendMessageToCurrentPlayer(self, message):
    self.s.sendto(json.dumps(message), self.game.currentTurn.connection)

  def sendMessageToPlayer(self, player, message):
    self.s.sendto(json.dumps(message), player.connection)

  def broadcastMessage(self, message):
    print message
    for p in self.game.connectedPlayers():
        self.s.sendto(json.dumps(message), p.connection)

  def printScore(self, score):
      s = ""
      for t in score:
          s += "Team {tidx}:\n".format(tidx = t.id)
          for p in t.players:
              s+= "-" + p.identifier + "\n"
          s+= "{pts} Points!".format(pts = t.score)
          s+= "\n"
      return s

  def checkEndGame(self):
      if(self.game.gameOver == True):
          self.broadcastMessage({'type': 'message', 'message': "Game Over!\n" + self.game.currentTurn.identifier + " has won the turn!\n"})
          score = self.game.getScore()
          for s in score:
              if(s.score > self.game.maxScore):
                  self.broadcastMessage({'type': 'message', 'message': "Game Over!\n" + "Team " + s.id + " has won the game!\n"})
          self.broadcastMessage({'type': 'message', 'message': self.printScore(score)})
          self.game.newGame()