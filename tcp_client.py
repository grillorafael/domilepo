import socket
import sys
import json
import os

class TcpClient:
  def __init__(self):
    self.messageTmp = ""
    self.stackMessage = []
    HOST = raw_input("Digite o IP destino (ex: 127.0.0.1)\n")
    PORT = int(raw_input("Digite a Porta (ex: 3000):\n"))
    #HOST, PORT = "127.0.0.1", 3000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      sock.connect((HOST, PORT))
      while 1:
        self.formMessage(sock.recv(1024), sock)
    finally:
      sock.close()

  def handleMessage(self, message, sock):
    message = json.loads(message)
    print message['message']
    if(message['type'] == 'options'):
      option = raw_input(message['question'])
      sock.send(json.dumps({'type': 'options', 'selected': option}))
    elif(message['type'] == 'piece'):
      option = raw_input(message['question'])
      sock.send(json.dumps({'type': 'piece', 'selected': option}))
    elif(message['type'] == 'position'):
      option = raw_input(message['question'])
      sock.send(json.dumps({'type': 'position', 'selected': option}))

  def formMessage(self, r, sock):
    for c in r:
      self.messageTmp = self.messageTmp + c
      if c == '{':
        self.stackMessage.append('{')
      elif c == '}':
        self.stackMessage.pop()

      if len(self.stackMessage) == 0:
        fullMessage = self.messageTmp
        self.messageTmp = ""
        self.handleMessage(fullMessage, sock)

TcpClient()
