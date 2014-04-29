class Colors:
  GREEN = '\033[0;32m'
  BLUE = '\033[0;34m'
  RED = '\033[0;31m'
  ENDC = '\033[0m'

  @staticmethod
  def green(str):
    return Colors.GREEN + str + Colors.ENDC
  @staticmethod
  def blue(str):
    return Colors.BLUE + str + Colors.ENDC
  @staticmethod
  def red(str):
    return Colors.BLUE + str + Colors.ENDC
