import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import statistics 

text_type = sys.argv[1]

with open(text_type) as csvfile:
        reader = csv.reader(csvfile)
        total_guesses = 0
        total_correct_guesses = 0
        total_time = 0
        for row in reader:
                if row[0][0:5] == "Total":
                    total_time += float(row[0][19:])
                else:
                    total_guesses += 1
                    if row[int(1)] == row[int(2)]:
                        total_correct_guesses +=1
        print("Accuracy: " + str(total_correct_guesses/total_guesses))
        print("Total attack time: " + str(total_time))