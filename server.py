import os
from game import *
from terminal_colors import *
from tcp_server import *
from udp_server import *

def askForTransportMethod(invalid = False):
  os.system('clear')
  if(invalid):
      print Colors.red("Please enter a valid option...\n")
  print Colors.blue('Select your transport method:') + "\n"
  print Colors.green('(1) TCP') + "\n"
  print Colors.green('(2) UDP') + "\n"
  selected = raw_input("")

  if(not selected.isdigit()):
      return askForTransportMethod(True)

  selected = int(selected)

  if selected == 1:
    return TcpServer
  elif selected == 2:
    return UdpServer
  else:
    return askForTransportMethod(True)

def askForPlayersSize():
    print Colors.blue('How many players?:') + "\n"
    print Colors.green('(1) 2 Players \n')
    print Colors.green('(2) 4 Players \n')
    selected = raw_input("")
    if(selected.isdigit()):
        selected = int(selected)
        if selected == 1 or selected == 2:
            return selected * 2

    print Colors.red('Wrong option\n')
    return askForPlayersSize()

def initGame(Server):
  print Colors.blue("Welcome to DomiLepo!")
  game = DomiLepo(askForPlayersSize())
  server = Server(game)

initGame(askForTransportMethod())
