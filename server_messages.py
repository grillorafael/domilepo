from terminal_colors import *
import json

class ServerMessages(object):
    def __init__(self):
        self.lastPiece = None

    def handleData(self, data):
        if data:
            if(not data['selected']):
                self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Please input a valid option.\n"})
                return True
            if(data['type'] == 'options'):
                if(data['selected'] == '1'):
                    self.showCurrentPlayerPieces()
                elif(data['selected'] == '2'):
                    self.showToCurrentPlayerGamePieces()
                    self.askCurrentPlayerToPlay()
                elif(data['selected'] == '3'):
                    self.showToCurrentPlayerGameHeads()
                    self.askCurrentPlayerToPlay()
                elif(data['selected'] == '4'):
                    self.showToCurrentPlayerPlayersPieceCount()
                    self.askCurrentPlayerToPlay()
                else:
                    self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Invalid Option!\n"})
                    return True
            elif(data['type'] == 'position'):
                if(data['selected'] == '0' or data['selected'] == '1'):
                    colorsPrintMethod = getattr(Colors, self.game.currentTurn.identifier.lower())
                    self.broadcastMessage({'type': 'message', 'message': colorsPrintMethod("{}".format(self.game.currentTurn.identifier.upper())) + " has played [{head},{tail}].\n".format(head=self.lastPiece[0], tail=self.lastPiece[1])})
                    #self.broadcastMessage({'type': 'message', 'message': self.game.currentTurn.identifier.upper() + " has played [{head},{tail}].\n".format(head=self.lastPiece[0], tail=self.lastPiece[1])})

                    self.game.playPiece(self.lastPiece, int(data['selected']))
                    self.checkEndGame()
                    return True
                else:
                    self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Invalid Option\n"})
                    self.askCurrentPlayerToPlay()
            elif(data['type'] == 'piece'):
                pieceIdx = data['selected'].replace('p', '')
                if pieceIdx == 'b':
                    return True
                elif pieceIdx == 'e':
                    if(self.game.canDraw()):
                        self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Can't skip yet!\n"})
                    else:
                        self.game.skipCount += 1
                        if(not self.game.setNextTurn()):
                            self.broadcastMessage({'type': 'message', 'message': "Draw! Checking points....\n"})
                        self.checkEndGame()
                    return True
                elif pieceIdx == 'd':
                    if(self.game.canDraw()):
                        self.game.drawPiece()
                        self.broadcastMessage({'type': 'message', 'message': self.game.currentTurn.identifier.upper() + " has drawn a domino.\n"})
                        self.sendMessageToCurrentPlayer({'type': 'message', 'message': "You got the "+ self.game.currentTurn.printPiece(len(self.game.currentTurn.pieces)-1) + "!\n"})
                    else:
                        self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Can't draw any more pieces.\n"})
                    return True
                if(not pieceIdx.isdigit()):
                    self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Please input a valid option.\n"})
                    return True
                piece = self.game.currentTurn.getPieceByIdx(int(pieceIdx))
                self.lastPiece = piece
                if piece == False:
                    self.sendMessageToCurrentPlayer({'type': 'message', 'message': "Invalid Piece\n"})
                    self.askCurrentPlayerToPlay()
                else:
                    possiblePiecePositions = list(self.game.canUsePiece(piece))
                    if len(possiblePiecePositions) > 0:
                        if len(possiblePiecePositions) == 1:
                            colorsPrintMethod = getattr(Colors, self.game.currentTurn.identifier.lower())
                            self.broadcastMessage({'type': 'message', 'message': colorsPrintMethod("{}".format(self.game.currentTurn.identifier.upper())) + " has played [{head},{tail}].\n".format(head=piece[0], tail=piece[1])})
                            #self.broadcastMessage({'type': 'message', 'message': self.game.currentTurn.identifier.upper() + " has played [{head},{tail}].\n".format(head=piece[0], tail=piece[1])})
                            self.game.playPiece(piece, possiblePiecePositions[0])
                            self.checkEndGame()
                            return True
                        else:
                            self.askPlayerToChoosePosition()
                    else:
                        self.sendMessageToCurrentPlayer({'type': 'message', 'message': "You cannot use this piece\n"})
                        self.askCurrentPlayerToPlay()
        return False

    def askPlayerToChoosePosition(self):
        self.sendMessageToCurrentPlayer({'type': 'position', 'message': 'Please choose the piece position', 'question': '(0) for {}\n(1) for {}\n'.format(self.game.heads[0], self.game.heads[1])})

    def showToCurrentPlayerPlayersPieceCount(self):
        text = ""
        for p in self.game.players:
            colorsPrintMethod = getattr(Colors, p.identifier.lower())
            text  = text + "{0}: {1} pieces\n".format(colorsPrintMethod(p.identifier.upper()), len(p.pieces))
        self.sendMessageToCurrentPlayer({'type': 'message', 'message': text})

    def showToCurrentPlayerGameHeads(self):
        self.sendMessageToCurrentPlayer({'type': 'message', 'message': Colors.red("Heads:") + " {0} {1}".format(self.game.heads[0], self.game.heads[1])})

    def showToCurrentPlayerGamePieces(self):
        self.sendMessageToCurrentPlayer({'type': 'message', 'message': self.game.printGamePieces()})

    def showCurrentPlayerPieces(self):
        if self.game.canDraw():
            self.sendMessageToCurrentPlayer({'type': 'piece', 'message': self.game.currentTurn.piecesOptions(), 'question': "Please choose a piece to play:  (Press 'd' to draw one domino or 'b' to go back)\n"})
        else:
            self.sendMessageToCurrentPlayer({'type': 'piece', 'message': self.game.currentTurn.piecesOptions(), 'question': "Please choose a piece to play:  (Press 'e' to skip your turn or 'b' to go back)\n"})

    def askCurrentPlayerToPlay(self):
        self.showToCurrentPlayerGameHeads()
        self.sendMessageToCurrentPlayer({'type': 'options', 'message': self.playerOptions(), 'question': "Please choose a option:\n"})

    def playerOptions(self):
        return Colors.blue("(1)") + " Your pieces\n" + Colors.blue("(2)") + " Pieces in game\n" + Colors.blue("(3)") + " Shows heads\n" + Colors.blue("(4)") + " Show players piece count"

    def sendMessageToCurrentPlayer(self, message):
        raise NotImplementedError, ""

    def sendMessageToPlayer(self, player, message):
        raise NotImplementedError, ""

    def broadcastMessage(self, message):
        raise NotImplementedError, ""

    def receiveData(self):
        raise NotImplementedError, ""

    def printScore(self, score):
        s = ""
        for t in score:
            s += "Team {tidx}:\n".format(tidx = t.id)
            for p in t.players:
                s+= "-" + p.identifier + "\n"
            s+= "{pts} Points!".format(pts = t.score)
            s+= "\n"
        return s

    def checkEndGame(self):
        if(self.game.gameOver == True):
            if(self.game.currentTurn == None):
                self.broadcastMessage({'type': 'message', 'message': "Game Over!\nSame score! 0 points this round!\n"})
            else:
                self.broadcastMessage({'type': 'message', 'message': "Game Over!\n" + self.game.currentTurn.identifier + " has won the turn!\n"})
            score = self.game.getScore()
            for s in score:
                if(s.score >= self.game.maxScore):
                    self.broadcastMessage({'type': 'message', 'message': "Game Over!\n" + "Team " + s.id + " has won the game!\n"})
            placar = self.printScore(score)
            print placar
            self.broadcastMessage({'type': 'message', 'message': placar})
            self.game.newGame()
