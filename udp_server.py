#!/usr/bin/python
from socket import *
from terminal_colors import *
from server_messages import *
import json, random, threading, thread

class UdpServer(ServerMessages):
    def __init__(self, game):
        super(ServerMessages, self).__init__()
        self.game = game

        self.s = socket(AF_INET, SOCK_DGRAM)
        self.s.bind(('127.0.0.1', 12000))

        print "Listening to 127.0.0.1:12000\n"


        self.packagesQueue = []
        self.timeout = 2000 #ms
        self.packageWaitingForAck = None
        #self.lastPackageId = False # False // True instead of 0//1
        self.happeningTimeout = None


        while 1:
            if(self.game.readyToStart()):
                colorsPrintMethod = getattr(Colors, self.game.currentTurn.identifier.lower())

                self.sendMessageToCurrentPlayer({'type': 'message', 'message': "It's your turn"})
                self.broadcastMessage({'type': 'message', 'message': colorsPrintMethod("------- {} PLAYER TURN -----".format(self.game.currentTurn.identifier.upper()))})
                self.askCurrentPlayerToPlay()
                while not self.receiveData():
                    continue
            else:
                msg, address = self.s.recvfrom(2048)

                player = self.game.getPlayerbySocket(address)
                if(player == None):
                    player = self.game.connectPlayer(address)
                elif(player.lastPackageSent == json.loads(msg)):
                    print "Discharging package"
                    self.ackFor(address, json.loads(msg))
                    continue
                jsonMsg = json.loads(msg)
                if(jsonMsg['type']!='ack'):
                    if(jsonMsg['type']!='join'):
                        self.ackFor(address, jsonMsg)
                    else:
                        player.lastPackageSent = jsonMsg
                        colorsPrintMethod = getattr(Colors, player.identifier.lower())
                        playerId = colorsPrintMethod(player.identifier.upper())
                        print jsonMsg
                        self.sendMessageToPlayer(player, {'type': 'message', 'message': "You are the {} player".format(playerId)})
                        self.broadcastMessage({'type': 'message', 'message': "{} player connected".format(playerId)})
                        self.broadcastMessage({'type': 'message', 'message': "Waiting for {} players to connect...".format(len(self.game.pendingConnectionPlayers()))})
                else:
                    self.ackMessage(address, jsonMsg)

    def sendMessageToCurrentPlayer(self, message):
        #self.s.sendto(json.dumps(message), self.game.currentTurn.connection)
        self.queueMessage(self.game.currentTurn.connection, message)



    def sendMessageToPlayer(self, player, message):
        self.queueMessage(player.connection, message)
        #self.s.sendto(json.dumps(message), player.connection)

    def ackFor(self, sender, data):
        if(data['type'] == 'ack'):
            return False
        if(random.random() > 0.0):
            print "Sending ack for ", sender, data
            player = self.game.getPlayerbySocket(sender)

            if(player.waitingForAck == data['identifier']):
                messageToSend = { 'type': 'ack', 'message': "", 'packageId': data['identifier'] }
                self.s.sendto(json.dumps(messageToSend), sender)
                player.waitingForAck = not player.waitingForAck
                print "Sent!"
                return True
            return False
        else:
            print "Not sending ACK"
            return True


    def broadcastMessage(self, message):
        for p in self.game.connectedPlayers():
            self.queueMessage(p.connection, message.copy())

    def receiveData(self):
        while 1:
            data, sender = self.s.recvfrom(1024)
            data = json.loads(data)

            if(not self.ackFor(sender, data)):
                self.ackMessage(sender, data)
                return False

            player = self.game.getPlayerbySocket(sender)
            if(player.lastPackageSent == data):
                return False

            player.lastPackageSent = data
            if(self.handleData(data)):
                return True

    def queueMessage(self, connection, message):
        player = self.game.getPlayerbySocket(connection)
        message['identifier'] = player.state
        print "Empilhando:", message,"\nPara:", connection, "\n"
        player.state = not player.state
        self.packagesQueue.append((message, connection))
        self.setNextPackage()


    def setNextPackage(self):
        print len(self.packagesQueue)
        if(len(self.packagesQueue) > 0 and self.packageWaitingForAck == None):
            self.packageWaitingForAck = self.packagesQueue[0]
            print "Esperando:", self.packageWaitingForAck[0], "Do:", self.packageWaitingForAck[1], "\n";

            self.happeningTimeout = threading.Timer(self.timeout / 1000, self.sendPendingPackage)
            self.happeningTimeout.start()
            self.sendPendingPackage(False)

    def sendPendingPackage(self, retransmition = True):
        if(retransmition):
           self.happeningTimeout = threading.Timer(self.timeout / 1000, self.sendPendingPackage)
           self.happeningTimeout.start()
           print "Retransmiting package"
        print "sendPendingPackage", self.packageWaitingForAck;
        if(not (self.packageWaitingForAck[0] == None)):
            self.s.sendto(json.dumps(self.packageWaitingForAck[0]), self.packageWaitingForAck[1])

    def ackMessage(self, connection, message):
        print "Receiving ack for ", message, connection
        self.happeningTimeout.cancel()
        self.packageWaitingForAck = None
        self.packagesQueue.pop(0) # Removing que first element
        self.setNextPackage()
