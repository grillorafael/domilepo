import os
from game import *
from terminal_colors import *
from tcp_client import *
from udp_client import *

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
    return TcpClient
  elif selected == 2:
    return UdpClient
  else:
    return askForTransportMethod(True)

def initGame(Method):
  print Colors.blue("Welcome to DomiLepo! ({})".format(Method.TITLE))
  Method()

initGame(askForTransportMethod())
