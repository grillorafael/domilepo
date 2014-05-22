from socket import *
import time, threading, json, thread

class UdpClient:

    def __init__(self):
        self.messageTmp = ""
        self.stackMessage = []

        self.lastTimeoutRetransmition = None

        self.packagesQueue = []
        self.timeout = 5000 #ms
        self.packageWaitingForAck = None
        self.lastPackageId = False # False // True instead of 0//1
        self.happeningTimeout = None

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

            self.happeningTimeout = threading.Timer(self.timeout / 1000, self.sendPendingPackage)
            self.happeningTimeout.start()

            self.sendPendingPackage(False)

    def sendPendingPackage(self, retransmition = True):
        if(retransmition):
            self.happeningTimeout = threading.Timer(self.timeout / 1000, self.sendPendingPackage)
            self.happeningTimeout.start()

            print "Retransmiting package"
        print "sendPendingPackage"
        if(not (self.packageWaitingForAck == None)):
            self.sock.sendto(json.dumps(self.packageWaitingForAck), self.sv)

    def sendMessage(self, message):
        self.queueMessage(message)

    def typeMessage(self, message):
        option = raw_input(message['question'])
        self.sendMessage({'type': 'options', 'selected': option})

    def optionsMessage(self, message):
        option = raw_input(message['question'])
        self.sendMessage({'type': 'piece', 'selected': option})

    def positionMessage(self, message):
        option = raw_input(message['question'])
        self.sendMessage({'type': 'position', 'selected': option})

    def ackMessage(self, message):
        print "Receiving ack for ", message
        self.happeningTimeout.cancel()
        self.packageWaitingForAck = None
        self.packagesQueue.pop(0) # Removing que first element
        self.setNextPackage()

    def handleMessage(self, message):
        message = json.loads(message)
        print message
        print message['message']
        func = None
        if(message['type'] == 'options'):
            thread.start_new_thread(self.typeMessage, (message, ))
        elif(message['type'] == 'piece'):
            thread.start_new_thread(self.optionsMessage, (message, ))
        elif(message['type'] == 'position'):
            thread.start_new_thread(self.positionMessage, (message, ))
        elif(message['type'] == 'ack' and message['packageId'] == self.packageWaitingForAck['identifier']):
            thread.start_new_thread(self.ackMessage, (message, ))
        # else:
            # Retransmit last package
            # Talvez tenha que retransmitir
            # self.sendPendingPackage()

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
