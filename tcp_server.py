#!/usr/bin/python
from socket import *

class TcpServer:
  def __init__(self, game):
    self.game = game

    s = socket(AF_INET, SOCK_STREAM)    # create a TCP socket
    s.bind(('127.0.0.1', 3000))            # bind it to the server port
    s.listen(5)                         # allow 5 simultaneous # pending connections
    print "Listening to http://127.0.0.1:3000\n"

    while 1:
        # wait for next client to connect
        connection, address = s.accept() # connection is a new socket
        self.game.connectPlayer(connection)
        self.broadcastMessage("New player connected\n")
        self.broadcastMessage("Waiting for more players to connect...\n")

        # while 1:
        #     data = connection.recv(1024) # receive up to 1K bytes
        #     if data:
        #         connection.send('echo -> ' + data)
        #     else:
        #         break
        # connection.close()              # close socket

  def broadcastMessage(self, message):
    for p in self.game.connectedPlayers():
      print "{}\n".format(message)
      p.connection.send(message)
