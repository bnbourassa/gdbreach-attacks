import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import statistics 

text_type = sys.argv[1]

threshold = float(sys.argv[2])

case = sys.argv[3]

filename = sys.argv[4]

total_guesses = {'100': 0}
total_correct_guesses = {'100': 0}
total_times = {'100': []}
total_db_queries = {'100': []}

places = {}

totalCorrect = 0

with open(text_type) as csvfile:
        dbQueries = []
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0][0:1] == 'N':
                  dbQueries.append(float(row[0][22:]))
            if row[0][0:1] == 'S':
                 places[row[0][15:]] = 0 
                 currPlace = row[0][15:]
            if row[0][0:1] == 'P':
                 if row[0][-1:] == '1':
                       places[currPlace] = 1
        for i in places:
              if places[i] == 1:
                    totalCorrect += 1
        print(totalCorrect/50)
        print(statistics.mean(dbQueries))