import csv
import numpy as np
# import matplotlib.pyplot as plt
from collections import defaultdict
import sys

thresholds = dict()
thresholds['zlib'] = 0.51

text_type = sys.argv[1].replace('--', '')

ref_scores = defaultdict(lambda: [])
true_labels = defaultdict(lambda: [])

with open(text_type + '.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row[0]=="0" or row[0]=="1":
            true_labels[int(row[1])].append(int(row[0]))
            ref_scores[int(row[1])].append((int(row[2]) if row[2] != "0" else 1, int(row[3]), int(row[4])))

threshold = thresholds['zlib']
accuracies = []

for records_on_page in ref_scores.keys():
    pcts = [1 - (b_yes - b) / max(b_yes - b_no, 1) for b_no, b, b_yes in ref_scores[records_on_page]]
    labels = np.array([pct >= threshold for pct in pcts])
    accuracy = 1 - np.sum(np.abs(labels - true_labels[records_on_page])) / labels.shape[0]
    accuracies.append((records_on_page, accuracy))

accuracies.sort()

print('zlib' + ": " + str(accuracies))

# ax.plot([recs_on_page for recs_on_page, accuracy in accuracies], [accuracy for recs_on_page, accuracy in accuracies], label='zlib')
