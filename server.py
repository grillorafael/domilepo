import os
from game import *
from terminal_colors import *
from tcp_server import *
from udp_server import *

def askForTransportMethod():
  os.system('clear')
  print Colors.blue('Select your transport method:') + "\n"
  print Colors.green('(1) TCP') + "\n"
  print Colors.green('(2) UDP') + "\n"
  selected = int(raw_input(""))
  print selected
  if selected == 1:
    return TcpServer
  elif selected == 2:
    return UdpServer
  else:
    print "Please enter a valid option..."
    return askForTransportMethod()

def initGame(Server):
  print Colors.blue("Welcome to DomiLepo!")
  game = DomiLepo()
  server = Server(game)

initGame(askForTransportMethod())
