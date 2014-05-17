#!/usr/bin/python
from socket import *
from terminal_colors import *
from server_messages import *
import json

class TcpServer(ServerMessages):
    def __init__(self, game):
        super(ServerMessages, self).__init__()

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


    def sendMessageToCurrentPlayer(self, message):
        self.game.currentTurn.connection.send(json.dumps(message))

    def sendMessageToPlayer(self, player, message):
        player.connection.send(json.dumps(message))

    def broadcastMessage(self, message):
        for p in self.game.connectedPlayers():
            p.connection.send(json.dumps(message))

    def receiveData(self):
        while 1:
            data = self.game.currentTurn.connection.recv(1024)
            if(self.handleData(data)):
                return;
