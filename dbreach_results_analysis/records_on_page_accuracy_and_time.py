import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import statistics 

text_type = sys.argv[1]

threshold = float(sys.argv[2])

case = sys.argv[3]

percent = sys.argv[4]

filename = sys.argv[5]

fig, ax = plt.subplots()
ax.set(xlabel="threshold", ylabel="accuracy", title="Accuracy of decision attack for different threshold values")
for c in ["snappy"]:
    true_labels = {'1': [], '20': [], '40': [], '60': [], '80': [], '100': [], '120': [], '140': [], '160': [], '180': [], '200': [], '220': [], '240': []}
    ref_scores = {'1': [], '20': [], '40': [], '60': [], '80': [], '100': [], '120': [], '140': [], '160': [], '180': [], '200': [], '220': [], '240': []}
    setup_times = {'1': [], '20': [], '40': [], '60': [], '80': [], '100': [], '120': [], '140': [], '160': [], '180': [], '200': [], '220': [], '240': []}
    guess_times = {'1': [], '20': [], '40': [], '60': [], '80': [], '100': [], '120': [], '140': [], '160': [], '180': [], '200': [], '220': [], '240': []}
    total_times = {'1': [], '20': [], '40': [], '60': [], '80': [], '100': [], '120': [], '140': [], '160': [], '180': [], '200': [], '220': [], '240': []}
    total_db_queries = {'1': [], '20': [], '40': [], '60': [], '80': [], '100': [], '120': [], '140': [], '160': [], '180': [], '200': [], '220': [], '240': []}
    accuracies = {'1': [], '20': [], '40': [], '60': [], '80': [], '100': [], '120': [], '140': [], '160': [], '180': [], '200': [], '220': [], '240': []}
    true_labels = {'1': [], '2': [], '3': [], '4': [], '5': []}
    ref_scores = {'1': [], '2': [], '3': [], '4': [], '5': []}
    setup_times = {'1': [], '2': [], '3': [], '4': [], '5': []}
    guess_times = {'1': [], '2': [], '3': [], '4': [], '5': []}
    total_times = {'1': [], '2': [], '3': [], '4': [], '5': []}
    total_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
    accuracies = {'1': [], '2': [], '3': [], '4': [], '5': []}

    total_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
    ref_scores_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
    guess_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
    setup_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}

    # true_labels = {'100': []}
    # ref_scores = {'100': []}
    # setup_times = {'100': []}
    # guess_times = {'100': []}
    # total_times = {'100': []}

    # total_db_queries = {'100': []}
    # ref_scores_db_queries = {'100': []}
    # guess_db_queries = {'100': []}
    # setup_queries = {'100': []}

    # accuracies = {'100': []}

    with open(text_type) as csvfile:
        reader = csv.reader(csvfile)
        # records_on_page = '100'
        for row in reader:
            if 'PERCENT' in row[0]:
                     records_on_page = row[0][25:]
            # print(records_on_page)
            if row[0] != '0' and row[0] != '1':
                if "Total DB Queries This Round:" not in row[0] and 'Total time spent this round in seconds:' not in row[0] and 'ref_score_db_queries' not in row[0] and 'true_label' not in row[0] and 'PERCENT' not in row[0] and 'QUERIES' not in row[0] and 'setup_queries' not in row[0]:
                    print(row)
                    setup_queries[records_on_page].append(float(row[0]))
                    ref_scores_db_queries[records_on_page].append(float(row[2]))
                    guess_db_queries[records_on_page].append(float(row[3]))
                    total_db_queries[records_on_page].append(float(row[4]))
            # if "Total DB Queries This Round:" in row[0]:
                    # total_db_queries[records_on_page].append(int(row[0][28:]))
            elif "Total time spent this round in seconds:" in row[0]:
                    total_times[records_on_page].append(float(row[0][39:]))
            else:
                if(row[0] == "0" or row[0] == "1"):
                    true_labels[records_on_page].append(int(row[0]))
                    ref_scores[records_on_page].append((int(row[2]) if row[2] != "0" else 1, int(row[3]), int(row[4])))
                else:
                    pass
                #print(row)
                # setup_times.append(float(row[5]))
                # guess_times.append(float(row[6]))

    # print(ref_scores)
    f = open(filename + ".csv", "a")
    # f.write('case,records on page,accuracy,average time,average number of queries\n')
    f.write(case + '\n')
    f.write('ACCURACIES\n')
    for i in true_labels:
        curr_true_labels = true_labels[i]
        curr_true_labels = np.array(curr_true_labels)
        pcts = [1 - (b - b_yes) / b_no for b_no, b, b_yes in ref_scores[i]]
        # threshold = 0.81
        # accuracies = []

        # thresholds = np.arange(-0.5, 1.5, 0.001)
        accuracies = []
        # for threshold in thresholds:
        #     labels = np.array([pct >= threshold for pct in pcts])
        #     accuracy = 1 - np.sum(np.abs(labels - curr_true_labels)) / labels.shape[0]
        #     accuracies.append(accuracy)

        # maximum_accuracy = accuracies[0]

        labels = np.array([pct >= threshold for pct in pcts])
        # print(labels)
        # print(curr_true_labels)
        accuracy = 1 - np.sum(np.abs(labels - curr_true_labels)) / labels.shape[0]
        accuracies.append(accuracy)
        # print(accuracies)
        f.write("("+str(i)+","+str(round(accuracies[0], 3))+")")

    # f.write('\nATTACK TIMES\n')
    # for i in true_labels:
    #     f.write("("+str(i)+","+str(round(statistics.mean(total_times[i]), 3))+")")
    # f.write('\nNUMBER OF DB QUERIES FOR REFERENCE SCORES\n')
    # for i in true_labels:
    #     f.write("("+str(i)+","+str(round(statistics.mean(ref_scores_db_queries[i]), 3))+")")
    # f.write('\nNUMBER OF DB QUERIES FOR GUESS SCORES\n')
    # for i in true_labels:
    #     f.write("("+str(i)+","+str(round(statistics.mean(guess_db_queries[i]), 3))+")")
    # f.write('\nNUMBER OF DB QUERIES\n')  
    # for i in true_labels:  
    #     f.write("("+str(i)+","+str(round(statistics.mean(total_db_queries[i]), 3))+")")
    # f.write('\n')
    # for i in true_labels:
    #      f.write(str(total_db_queries[i]))
    f.write('\nNUMBER OF DB QUERIES FOR SETUP\n')
    for i in true_labels:
        f.write(str(round(statistics.mean(setup_queries[i]), 3)) + "\n")
    f.write('\nNUMBER OF DB QUERIES FOR REFERENCE SCORES\n')
    for i in true_labels:
        f.write(str(round(statistics.mean(ref_scores_db_queries[i]), 3))+"\n")
    f.write('\nNUMBER OF DB QUERIES FOR GUESS SCORES\n')
    for i in true_labels:
        f.write(str(round(statistics.mean(guess_db_queries[i]), 3))+"\n")
    f.write('\nNUMBER OF DB QUERIES\n')  
    for i in true_labels:  
        f.write(str(round(statistics.mean(total_db_queries[i]), 3))+"\n")
    f.write('\n')
    for i in true_labels:
         f.write(str(total_db_queries[i]))

    # f = open("english_baseline_vs_binary_latex_code.tex", "w")
    # f.write("\\addplot[color=blue,mark=none]\n")
    # f.write("coordinates{")
        # f = open("random_ten_percent_grouping_data.csv", "a").write("random_snappy_baseline\n,"+str(i)+","+str(round(accuracies[0], 3))+","+str(round(statistics.mean(total_times[i]), 3))+","+str(round(statistics.mean(total_db_queries[i]), 3))+"\n")
        # print(i + ": " + str(accuracies))
        # print(statistics.mean(total_times[i]))
        # print(statistics.mean(total_db_queries[i]))
