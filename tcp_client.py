import socket
import sys

HOST, PORT = "127.0.0.1", 3000
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    while True:
      dataToSend = raw_input("Please, enter data\n")
      sock.sendall(dataToSend + "\n")
      # Receive data from the server and shut down
      received = sock.recv(1024)
      print "Sent:     {}".format(dataToSend)
      print "Received: {}".format(received)
finally:
    sock.close()
