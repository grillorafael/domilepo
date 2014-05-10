import socket
import sys
import json
import os

def handleMessage(message, sock):
  message = json.loads(message)

  if(message['type'] == 'message'):
    print message['message']
  elif(message['type'] == 'options'):
    os.system('clear')
    print message['message']
    option = raw_input("Please, enter your option\n")
    sock.send(json.dumps({'type': 'options', 'selected': option}))

def formMessage(r, chunks, stackMessage, sock):
  for c in r:
    chunks = chunks + c
    if c == '{':
      stackMessage.append('{')
    elif c == '}':
      stackMessage.pop()

    if len(stackMessage) == 0:
      fullMessage = chunks
      chunks = ""
      handleMessage(fullMessage, sock)

def main():
  HOST, PORT = "127.0.0.1", 3000
  chunks = ""
  stackMessage = []

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((HOST, PORT))
    while 1:
      formMessage(sock.recv(1024), chunks, stackMessage, sock)
  finally:
    sock.close()


main()
