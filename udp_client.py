from socket import *
import json

class UdpClient:

  def __init__(self):
    self.messageTmp = ""
    self.stackMessage = []

    port = 12000
    HOST, PORT = "127.0.0.1", int(port)
    sv = (HOST, port)
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.sendto("{}", sv)
    try:
        while 1:
            msg =  sock.recv(1024)
            self.formMessage(msg, sock, sv)
    finally:
        sock.close()

  def handleMessage(self, message, sock, sv):
    message = json.loads(message)
    print '------------ NEW INTERACTION ---------'
    print message['message']
    if(message['type'] == 'options'):
      option = raw_input(message['question'])
      sock.sendto(json.dumps({'type': 'options', 'selected': option}),sv)
    elif(message['type'] == 'piece'):
      option = raw_input(message['question'])
      sock.sendto(json.dumps({'type': 'piece', 'selected': option}),sv)
    elif(message['type'] == 'position'):
      option = raw_input(message['question'])
      sock.sendto(json.dumps({'type': 'piece', 'selected': option}), sv)

  def formMessage(self, r, sock, sv):
    for c in r:
      self.messageTmp = self.messageTmp + c
      if c == '{':
        self.stackMessage.append('{')
      elif c == '}':
        self.stackMessage.pop()

      if len(self.stackMessage) == 0:
        fullMessage = self.messageTmp
        self.messageTmp = ""
        self.handleMessage(fullMessage, sock, sv)

UdpClient()