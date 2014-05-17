#!/usr/bin/python
from socket import *
from terminal_colors import *
from server_messages import *
import json

class UdpServer(ServerMessages):
    def __init__(self, game):
        super(ServerMessages, self).__init__()
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


    def sendMessageToCurrentPlayer(self, message):
        self.s.sendto(json.dumps(message), self.game.currentTurn.connection)

    def sendMessageToPlayer(self, player, message):
        self.s.sendto(json.dumps(message), player.connection)

    def broadcastMessage(self, message):
        print message
        for p in self.game.connectedPlayers():
            self.s.sendto(json.dumps(message), p.connection)

    def receiveData(self):
        while 1:
            data, sender = self.s.recvfrom(1024)
            if(self.handleData(data)):
                return;
