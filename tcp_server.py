# REFERENCE: https://docs.python.org/2.7/library/socketserver.html
import SocketServer
from socket import *
from terminal_colors import *

class TcpHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    # self.request is the TCP socket connected to the client
    self.data = self.request.recv(1024).strip()
    print "{} wrote:".format(self.client_address[0])
    print self.data
    # just send back the same data, but upper-cased
    self.request.sendall(self.data.upper())

class TcpServer:
  def __init__(self):
    HOST, PORT = "127.0.0.1", 3000

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), TcpHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print Colors.red("Server started at: http://{HOST}:{PORT}".format(HOST=HOST, PORT=PORT))
    server.serve_forever()
