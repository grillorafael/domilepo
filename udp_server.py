#!/usr/bin/python
from socket import *
from terminal_colors import *
from server_messages import *
import json, random

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

                print "Receiving", msg, " from ", address

                player = self.game.getPlayerbySocket(address)
                if(player == None):
                    player = self.game.connectPlayer(address)
                    self.ackFor(address, json.loads(msg))
                elif(player.lastPackageSent == json.loads(msg)):
                    print "Discharging package"
                    self.ackFor(address, json.loads(msg))
                    # Descartando pacotes atrasados
                    continue

                player.lastPackageSent = json.loads(msg)

                self.sendMessageToPlayer(player, {'type': 'message', 'message': "You are the {} player".format(player.identifier.upper())})
                self.broadcastMessage({'type': 'message', 'message': "{} player connected".format(player.identifier.upper())})
                self.broadcastMessage({'type': 'message', 'message': "Waiting for {} players to connect...".format(len(self.game.pendingConnectionPlayers()))})

    def sendMessageToCurrentPlayer(self, message):
        self.s.sendto(json.dumps(message), self.game.currentTurn.connection)

    def sendMessageToPlayer(self, player, message):
        self.s.sendto(json.dumps(message), player.connection)

    def ackFor(self, sender, data):
        if(random.random() > 0.5):
            print "Sending ack for ", sender, data
            player = self.game.getPlayerbySocket(sender)

            if(player.waitingForAck == data['identifier']):
                messageToSend = { 'type': 'ack', 'message': "", 'packageId': data['identifier'] }
                self.s.sendto(json.dumps(messageToSend), sender)
                player.waitingForAck = not player.waitingForAck
        else:
            print "Not sending ACK"

    def broadcastMessage(self, message):
        print message
        for p in self.game.connectedPlayers():
            self.s.sendto(json.dumps(message), p.connection)

    def receiveData(self):
        while 1:
            data, sender = self.s.recvfrom(1024)
            print "Receiving", data, " from ", sender
            data = json.loads(data)

            self.ackFor(sender, data)

            player = self.game.getPlayerbySocket(sender)
            if(player.lastPackageSent == data):
                print "Last received message was ", player.lastPackageSent
                print "Discharging package"
                # Descartando pacotes atrasados de outros jogadores e pacotes duplicados
                return

            player.lastPackageSent = data
            if(self.handleData(data)):
                return
