#!/usr/bin/python
import os
from socket import *
from terminal_colors import *
import json

class TcpServer:
  def __init__(self, game):
    self.game = game

    self.s = socket(AF_INET, SOCK_STREAM)
    self.s.bind(('127.0.0.1', 3000))
    self.s.listen(5)

    print "Listening to 127.0.0.1:3000\n"

    while 1:
      if(self.game.readyToStart()):
        self.sendMessageToCurrentPlayer({'type': 'message', 'message': "It's your turn"})
        self.broadcastMessage({'type': 'message', 'message': "------- {} PLAYER TURN -----".format(self.game.currentTurn.identifier.upper())})
        self.askCurrentPlayerToPlay()
        self.receiveData()
      else:
        connection, address = self.s.accept()
        self.game.connectPlayer(connection)

        player = self.game.getPlayerbySocket(connection)

        self.sendMessageToPlayer(player, {'type': 'message', 'message': "You are the {} player".format(player.identifier.upper())})
        self.broadcastMessage({'type': 'message', 'message': "{} player connected".format(player.identifier.upper())})
        self.broadcastMessage({'type': 'message', 'message': "Waiting for {} players to connect...".format(len(self.game.pendingConnectionPlayers()))})

  def receiveData(self):
    while 1:
      data = self.game.currentTurn.connection.recv(1024)
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
            break
          else:
            self.sendMessageToCurrentPlayer("Invalid Option\n")
            self.askCurrentPlayerToPlay()
        elif(data['type'] == 'piece'):
          pieceIdx = data['selected'].replace('p', '')
          if pieceIdx == 'b':
            break
          elif pieceIdx == 'e':
            self.game.setNextTurn()
            break
          piece = self.game.currentTurn.getPieceByIdx(int(pieceIdx))
          if piece == False:
            self.sendMessageToCurrentPlayer("Invalid Piece\n")
            self.askCurrentPlayerToPlay()
          else:
            possiblePiecePositions = list(self.game.canUsePiece(piece))
            if len(possiblePiecePositions) > 0:
              if len(possiblePiecePositions) == 1:
                self.game.playPiece(piece, possiblePiecePositions[0])
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
      text  = text + "Player {0}: {1} pieces\n".format(p.identifier, len(p.pieces))
    self.sendMessageToCurrentPlayer({'type': 'message', 'message': text})

  def showToCurrentPlayerGameHeads(self):
    self.sendMessageToCurrentPlayer({'type': 'message', 'message': Colors.red("Heads:") + " {0} {1}".format(self.game.heads[0], self.game.heads[1])})

  def showToCurrentPlayerGamePieces(self):
    self.sendMessageToCurrentPlayer({'type': 'message', 'message': self.game.printGamePieces()})

  def showCurrentPlayerPieces(self):
    self.sendMessageToCurrentPlayer({'type': 'piece', 'message': self.game.currentTurn.piecesOptions(), 'question': "Please choose a piece to play:  (Press 'e' to skip your turn or 'b' to go back)\n"})

  def askCurrentPlayerToPlay(self):
    self.showToCurrentPlayerGameHeads()
    self.sendMessageToCurrentPlayer({'type': 'options', 'message': self.playerOptions(), 'question': "Please choose a option:\n"})

  def playerOptions(self):
    return Colors.blue("(1)") + " Your pieces\n" + Colors.blue("(2)") + " Pieces in game\n" + Colors.blue("(3)") + " Shows heads\n" + Colors.blue("(4)") + " Show players piece count"

  def sendMessageToCurrentPlayer(self, message):
    self.game.currentTurn.connection.send(json.dumps(message))

  def sendMessageToPlayer(self, player, message):
    player.connection.send(json.dumps(message))

  def broadcastMessage(self, message):
    for p in self.game.connectedPlayers():
      p.connection.send(json.dumps(message))
