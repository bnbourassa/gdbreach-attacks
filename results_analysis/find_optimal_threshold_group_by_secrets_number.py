import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import statistics 

text_type = sys.argv[1]

fig, ax = plt.subplots()
ax.set(xlabel="threshold", ylabel="accuracy", title="Accuracy of decision attack for different threshold values")
for c in ["snappy", "zlib", "lz4"]:
    true_labels = {'240': [], '220': [], '200': [], '180': [], '160': [], '140': [], '120': [], '100': [], '80': [], '60': [], '40': [], '20': [], '1': []}
    ref_scores = {'240': [], '220': [], '200': [], '180': [], '160': [], '140': [], '120': [], '100': [], '80': [], '60': [], '40': [], '20': [], '1': []}
    setup_times = {'240': [], '220': [], '200': [], '180': [], '160': [], '140': [], '120': [], '100': [], '80': [], '60': [], '40': [], '20': [], '1': []}
    guess_times = {'240': [], '220': [], '200': [], '180': [], '160': [], '140': [], '120': [], '100': [], '80': [], '60': [], '40': [], '20': [], '1': []}
    with open(text_type) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if(row[0] == "0" or row[0] == "1"):
                true_labels[row[1]].append(int(row[0]))
                ref_scores[row[1]].append((int(row[2]) if row[2] != "0" else 1, int(row[3]), int(row[4])))
            else:
                pass
                #print(row)
            setup_times[row[1]].append(float(row[5]))
            guess_times[row[1]].append(float(row[6]))
    
    f = open(text_type + "_" + c+"_threshold_data.csv", "w")
    for i in true_labels:
        curr_true_labels = true_labels[i]
        curr_true_labels = np.array(curr_true_labels)
        pcts = [1 - (b - b_yes) / b_no for b_no, b, b_yes in ref_scores[i]]
        # print(pcts)

        thresholds = np.arange(-0.5, 1.5, 0.001)
        accuracies = []
        for threshold in thresholds:
            labels = np.array([pct >= threshold for pct in pcts])
            accuracy = 1 - np.sum(np.abs(labels - curr_true_labels)) / labels.shape[0]
            accuracies.append(accuracy)

        ax.plot(thresholds, accuracies, label=c)

        maximum_accuracy = np.max(accuracies)
        maximum_threshold = -0.5 + 0.001*np.argmax(accuracies)
        print('secret number: ' + i)

        print(c + ": maximum accuracy achieved: " + str(maximum_accuracy))
        print(c + ": maximum accuracy threshold: " + str(maximum_threshold))

        avg_setup_time = statistics.mean(setup_times[i])
        avg_guess_time = statistics.mean(guess_times[i])
        print("Average setup time: ", statistics.mean(setup_times[i]))
        print("Average guess time: ", statistics.mean(guess_times[i]))

        # with open(c+"data_dump", 'w', newline='') as file:
        #     writer = csv.writer(file)
        #     writer.writerow(header)
        #     writer.writerow(data1)
        f.write(str(maximum_accuracy)+","+str(maximum_threshold)+","+str(avg_setup_time)+","+str(avg_guess_time) + "\n")

    #for threshold in thresholds:
     #   labels = np.array([pct >= threshold for pct in pcts])
      #  accuracy = 1 - np.sum(np.abs(labels - true_labels)) / labels.shape[0]
       # accuracies.append(accuracy)

   # ax.plot(thresholds, accuracies, label=c)
    
    # f = open(text_type + "_" + c+"_threshold_data.csv", "w")
    # f.write("threshold,accuracy\n")
    # for i in range(0,len(thresholds)):
    # 	f.write(str(thresholds[i])+","+str(accuracies[i]) + "\n")
    # f.close()
    # print(c + " thresholds: "+ str(thresholds))
    # print(c + " accuracies: "+ str(accuracies))

    #maximum_accuracy = np.max(accuracies)
    #maximum_threshold = -0.5 + 0.001*np.argmax(accuracies)
    #print(c + ": maximum accuracy achieved: " + str(maximum_accuracy))
    #print(c + ": maximum accuracy threshold: " + str(maximum_threshold))

    #print("Average setup time: ", statistics.mean(setup_times))
    #print("Average guess time: ", statistics.mean(guess_times))

    '''
    print("Errors:")
    labels = np.array([pct >= maximum_threshold for pct in pcts])
    for idx, label in enumerate(labels):
        l = 1 if label else 0
        if l != true_labels[idx]:
            print(str(idx) + "," + str(true_labels[idx]) + ": " + str(pcts[idx]))
    '''

# plt.legend()
# ax.grid()
# plt.savefig("threshold-accuracy.png")
# plt.show()

