from socket import *
import json

class UdpClient:

    def __init__(self):
        self.messageTmp = ""
        self.stackMessage = []

        self.packagesQueue = []
        self.timeout = 100 #ms
        self.packageWaitingForAck = None
        self.lastPackageId = False # False // True instead of 0//1

        port = 12000
        HOST, PORT = "127.0.0.1", int(port)
        self.sv = (HOST, PORT)
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sendMessage({})
        try:
            while 1:
                msg = self.sock.recv(1024)
                self.formMessage(msg)
        finally:
            self.sock.close()

    def queueMessage(self, message):
        message['identifier'] = not self.lastPackageId
        self.lastPackageId = not self.lastPackageId

        self.packagesQueue.append(message)
        self.setNextPackage()

    def setNextPackage(self):
        if(len(self.packagesQueue) > 0 and self.packageWaitingForAck == None):
            self.packageWaitingForAck = self.packagesQueue[0]
            self.sendPendingPackage()

    def sendPendingPackage(self):
        if(not (self.packageWaitingForAck == None)):
            self.sock.sendto(json.dumps(self.packageWaitingForAck), self.sv)

    def sendMessage(self, message):
        self.queueMessage(message)

    def handleMessage(self, message):
        message = json.loads(message)
        print message['message']
        if(message['type'] == 'options'):
            option = raw_input(message['question'])
            self.sendMessage({'type': 'options', 'selected': option})
        elif(message['type'] == 'piece'):
            option = raw_input(message['question'])
            self.sendMessage({'type': 'piece', 'selected': option})
        elif(message['type'] == 'position'):
            option = raw_input(message['question'])
            self.sendMessage({'type': 'position', 'selected': option})
        elif(message['type'] == 'ack' and message['packageId'] == self.packageWaitingForAck['identifier']):
            self.packageWaitingForAck = None
            self.packagesQueue.pop(0) # Removing que first element
            self.setNextPackage()
        else:
            # Retransmit last package
            self.sendPendingPackage()

    def formMessage(self, r):
        for c in r:
            self.messageTmp = self.messageTmp + c
            if c == '{':
                self.stackMessage.append('{')
            elif c == '}':
                self.stackMessage.pop()
            if len(self.stackMessage) == 0:
                fullMessage = self.messageTmp
                self.messageTmp = ""
                self.handleMessage(fullMessage)

UdpClient()
