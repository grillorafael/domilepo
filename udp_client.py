from socket import *
from terminal_colors import *
import time, threading, json, thread, json, random

class UdpClient:
    TITLE = 'UDP'
    def __init__(self):
        self.messageTmp = ""
        self.stackMessage = []

        self.lastTimeoutRetransmition = None

        self.packagesQueue = []
        self.timeout = 2000 #ms
        self.packageWaitingForAck = None
        self.lastPackageId = False # False // True instead of 0//1
        self.state = True # False // True instead of 0//1
        self.happeningTimeout = None

        HOST = raw_input(Colors.green("Digite o IP destino (ex: 127.0.0.1)\n"))
        PORT = raw_input(Colors.green("Digite a Porta (ex: 12000):\n"))

        if(PORT.isdigit()):
            PORT = int(PORT)
        else:
            print Colors.red("Something went wrong. Maybe the address isn't correct")
            return

        try:
            self.sv = (HOST, PORT)
            self.sock = socket(AF_INET, SOCK_DGRAM)
            self.sendMessage({'type': 'join'})
        except:
            print Colors.red("Something went wrong. Maybe the address isn't correct")
            return

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

            #print "Retransmiting package"
        #print "sendPendingPackage"
        if(not (self.packageWaitingForAck == None)):
            self.sock.sendto(json.dumps(self.packageWaitingForAck), self.sv)

    def sendMessage(self, message):
        #print "Sending", message
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
        #print "Receiving ack for ", message
        self.happeningTimeout.cancel()
        self.packageWaitingForAck = None
        self.packagesQueue.pop(0) # Removing que first element
        self.setNextPackage()

    def handleMessage(self, message):
        #print message
        message = json.loads(message)
        #print message
        func = None
        if(message['type'] == 'ack' and message['packageId'] == self.packageWaitingForAck['identifier']):
            thread.start_new_thread(self.ackMessage, (message, ))
        elif(self.ackFor(message)):
            print message['message']
            if(message['type'] == 'options'):
                thread.start_new_thread(self.typeMessage, (message, ))
            elif(message['type'] == 'piece'):
                thread.start_new_thread(self.optionsMessage, (message, ))
            elif(message['type'] == 'position'):
                thread.start_new_thread(self.positionMessage, (message, ))
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


    def ackFor(self, data):
        if(random.random() > 0.2):
            #print "Sending ack for ", self.sv, data
            if(self.state == data['identifier']):
                #print   "Acking"
                messageToSend = { 'type': 'ack', 'message': "", 'packageId': data['identifier'] }
                self.sock.sendto(json.dumps(messageToSend), self.sv)
                self.state = not self.state
                return True
            else:
                #print   "Reacking"
                messageToSend = { 'type': 'ack', 'message': "", 'packageId': data['identifier'] }
                self.sock.sendto(json.dumps(messageToSend), self.sv)
                return False
        else:
            print "Not sending ACK"
            if(self.state == data['identifier']):
                self.state = not self.state
                return True
            else:
                return False
