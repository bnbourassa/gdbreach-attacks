import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import statistics

text_type = sys.argv[1].replace("--", "")

threshold = float(sys.argv[2])

case = sys.argv[3]

filename = sys.argv[4]

fig, ax = plt.subplots()
ax.set(xlabel="threshold", ylabel="accuracy", title="Accuracy of decision attack for different threshold values")
for c in ["zlib"]:
    true_labels = {'100': []}
    ref_scores = {'100': []}
    setup_times = {'100': []}
    guess_times = {'100': []}
    total_times = {'100': []}
    total_db_queries = {'100': []}
    accuracies = {'100': []}

    true_labels = {'20': []}
    ref_scores = {'20': []}
    setup_times = {'20': []}
    guess_times = {'20': []}
    total_times = {'20': []}
    total_db_queries = {'20': []}
    accuracies = {'20': []}

    # true_labels = []
    # ref_scores = []
    with open(text_type) as csvfile:
        reader = csv.reader(csvfile)
        records_on_page = 0
        for row in reader:
            if len(row) > 1 and row[1] != records_on_page:
                records_on_page = row[1]
            # print(records_on_page)
            if "Number of DB Queries This Round:" in row[0]:
                    total_db_queries[records_on_page].append(int(row[0][33:]))
            elif "Time per round:" in row[0]:
                    total_times[records_on_page].append(float(row[0][15:]))
            if(row[0] == "0" or row[0] == "1"):
                true_labels[records_on_page].append(int(row[0]))
                ref_scores[records_on_page].append((int(row[2]) if row[2] != "0" else 1, int(row[3]), int(row[4])))
            else:
                pass

    f = open(filename + ".csv", "a")
    f.write(case + '\n')
    f.write('ACCURACIES\n')
    for i in true_labels:
         curr_true_labels = true_labels[i]
         curr_true_labels = np.array(curr_true_labels)
         pcts = [1 - (b_yes - b) / max(b_yes - b_no, 1) for b_no, b, b_yes in ref_scores[i]]

    # print(len(pcts))
         
        #  threshold = 0.49
         accuracies = []
        #  for threshold in thresholds:
         labels = np.array([pct >= threshold for pct in pcts])
         accuracy = 1 - np.sum(np.abs(labels - curr_true_labels)) / labels.shape[0]
         accuracies.append(accuracy)

    # ax.plot(thresholds, accuracies, label=c)
    
    # f = open(text_type + "_" + c+"_threshold_data.csv", "w")
    # f.write("threshold,accuracy\n")
    # for i in range(0,len(thresholds)):
    # 	f.write(str(thresholds[i])+","+str(accuracies[i]) + "\n")
    # f.close()

        #  maximum_accuracy = np.max(accuracies)
        #  maximum_threshold = -0.5 + 0.001*np.argmax(accuracies)
         print(str(round(accuracies[0], 3)))
         f.write("("+str(i)+","+str(round(accuracies[0], 3))+")")

    f.write('\nATTACK TIMES\n')
    for i in true_labels:
        f.write("("+str(i)+","+str(round(statistics.mean(total_times[i]), 3))+")")
        
    f.write('\nNUMBER OF DB QUERIES\n')  
    for i in true_labels:  
        f.write("("+str(i)+","+str(round(statistics.mean(total_db_queries[i]), 3))+")")
    f.write('\n')

#     print(c + ": maximum accuracy achieved: " + str(maximum_accuracy))
#     print(c + ": maximum accuracy threshold: " + str(maximum_threshold))

# plt.legend()
# ax.grid()
# plt.savefig("threshold-accuracy.png")
# plt.show()