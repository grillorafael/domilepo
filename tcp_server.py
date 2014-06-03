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
        self.s.bind(('', 3000))
        self.s.listen(5)

        print "Listening to port 3000\n"

        while 1:
            if(self.game.readyToStart()):
                colorsPrintMethod = getattr(Colors, self.game.currentTurn.identifier.lower())

                self.sendMessageToCurrentPlayer({'type': 'message', 'message': "It's your turn"})
                self.broadcastMessage({'type': 'message', 'message': colorsPrintMethod("------- {} PLAYER TURN -----".format(self.game.currentTurn.identifier.upper()))})
                self.askCurrentPlayerToPlay()
                self.receiveData()
            else:
                connection, address = self.s.accept()
                self.game.connectPlayer(connection)

                player = self.game.getPlayerbySocket(connection)

                colorsPrintMethod = getattr(Colors, player.identifier.lower())
                playerId = colorsPrintMethod(player.identifier.upper())

                self.sendMessageToPlayer(player, {'type': 'message', 'message': "You are the {} player".format(playerId)})
                self.broadcastMessage({'type': 'message', 'message': "{} player connected".format(playerId)})
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
            data = json.loads(data)
            if(self.handleData(data)):
                return;
