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
                colorsPrintMethod = getattr(Colors, self.game.currentTurn.identifier.lower())

                self.sendMessageToCurrentPlayer({'type': 'message', 'message': "It's your turn"})
                self.broadcastMessage({'type': 'message', 'message': colorsPrintMethod("------- {} PLAYER TURN -----".format(self.game.currentTurn.identifier.upper()))})
                self.askCurrentPlayerToPlay()
                self.receiveData()
            else:
                msg, address = self.s.recvfrom(2048)
                self.game.connectPlayer(address)

                self.ackFor(address, json.loads(msg))

                player = self.game.getPlayerbySocket(address)
                self.sendMessageToPlayer(player, {'type': 'message', 'message': "You are the {} player".format(player.identifier.upper())})
                self.broadcastMessage({'type': 'message', 'message': "{} player connected".format(player.identifier.upper())})
                self.broadcastMessage({'type': 'message', 'message': "Waiting for {} players to connect...".format(len(self.game.pendingConnectionPlayers()))})


    def sendMessageToCurrentPlayer(self, message):
        self.s.sendto(json.dumps(message), self.game.currentTurn.connection)

    def sendMessageToPlayer(self, player, message):
        self.s.sendto(json.dumps(message), player.connection)

    def ackFor(self, sender, data):
        print "Sending ack for ", sender, data
        messageToSend = { 'type': 'ack', 'message': "", 'packageId': data['identifier'] }
        self.s.sendto(json.dumps(messageToSend), sender)

    def broadcastMessage(self, message):
        print message
        for p in self.game.connectedPlayers():
            self.s.sendto(json.dumps(message), p.connection)

    def receiveData(self):
        while 1:
            data, sender = self.s.recvfrom(1024)
            data = json.loads(data)

            self.ackFor(sender, data)
            if(self.handleData(data)):
                return;
