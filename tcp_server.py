#!/usr/bin/python
import os
from socket import *
from terminal_colors import *
import json

class TcpServer:
  def __init__(self, game):
    self.game = game

    s = socket(AF_INET, SOCK_STREAM)    # create a TCP socket
    s.bind(('127.0.0.1', 3000))            # bind it to the server port
    s.listen(5)                         # allow 5 simultaneous # pending connections
    print "Listening to 127.0.0.1:3000\n"

    while 1:
        # wait for next client to connect
        connection, address = s.accept() # connection is a new socket
        self.game.connectPlayer(connection)
        self.broadcastMessage({'type': 'message', 'message': "New player connected"})
        if(self.game.readyToStart()):
          self.broadcastMessage({'type': 'message', 'message': "Game is ready to start"})
          self.sendMessageToCurrentPlayer({'type': 'message', 'message': "It's your turn"})
          self.sendMessageToCurrentPlayer({'type': 'options', 'message': self.playerOptions()})
          while 1:
            data = self.game.currentTurn.connection.recv(1024)
            if data:
              data = json.loads(data)
              if(data['type'] == 'options'):
                if(data['selected'] == '1'):
                  self.sendMessageToCurrentPlayer({'type': 'options', 'message': str(self.game.currentTurn.piecesOptions())})
                elif(data['selected'] == '2'):
                  self.sendMessageToCurrentPlayer({'type': 'options', 'message': str(self.game.usedPieces)})
        else:
          self.broadcastMessage({'type': 'message', 'message': "Waiting for {} players to connect...".format(len(self.game.pendingConnectionPlayers()))})
        # while 1:
        #     data = connection.recv(1024) # receive up to 1K bytes
        #     if data:
        #         connection.send('echo -> ' + data)
        #     else:
        #         break
        # connection.close()              # close socket

  def playerOptions(self):
    return "(1) Your pieces\n(2) Pieces in game"

  def sendMessageToCurrentPlayer(self, message):
    self.game.currentTurn.connection.send(json.dumps(message))

  def broadcastMessage(self, message):
    for p in self.game.connectedPlayers():
      p.connection.send(json.dumps(message))
