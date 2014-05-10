import socket
import sys

HOST, PORT = "127.0.0.1", 3000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((HOST, PORT))
    while 1:
      # dataToSend = raw_input("Please, enter data\n")
      # sock.sendall(dataToSend + "\n")
      received = sock.recv(1024)
      print received
      # print "Sent:     {}".format(dataToSend)
finally:
    sock.close()
