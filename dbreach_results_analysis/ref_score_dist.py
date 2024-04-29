import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import statistics 

text_type = sys.argv[1]

# filename = sys.argv[2]

c_yes = {}
c_no = {}

with open(text_type) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if 'YES' in row[0]:
                  for i in range(1, len(row)):
                        row[i] = row[i].strip('{')
                        row[i] = row[i].strip('}')
                        row[i] = row[i].strip(" ")
                        col_idx = row[i].find(":")
                        key = int(row[i][0:col_idx])
                        score = int(row[i][col_idx+2:])
                        if key in c_yes:
                              c_yes[key].append(score)
                        else:
                              c_yes[key] = [score]
            if 'NO' in row[0]:
                  for i in range(1, len(row)):
                        row[i] = row[i].strip('{')
                        row[i] = row[i].strip('}')
                        row[i] = row[i].strip(" ")
                        col_idx = row[i].find(":")
                        key = int(row[i][0:col_idx])
                        score = int(row[i][col_idx+2:])
                        if key in c_no:
                              c_no[key].append(score)
                        else:
                              c_no[key] = [score]
print("YES")
for i in c_yes:
      print("("+str(i)+","+str(statistics.mean(c_yes[i]))+")")

print("NO")
for i in c_no:
      print("("+str(i)+","+str(statistics.mean(c_no[i]))+")")
        # print(totalCorrect/50)
        # print(statistics.mean(dbQueries))