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

total_guesses = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0}
total_correct_guesses = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0}
total_times = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
total_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}

ref_scores_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
guess_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
grouping_queries = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
individual_guess_queries = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
total_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}

total_guesses = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
total_correct_guesses = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
total_times = {'1': [], '2': [], '3': [], '4': [], '5': []}
total_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}

ref_scores_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
guess_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
grouping_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
individual_guess_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
total_db_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}
setup_queries = {'1': [], '2': [], '3': [], '4': [], '5': []}

with open(text_type) as csvfile:
        reader = csv.reader(csvfile)
        records_on_page = 0
        for row in reader:
                if 'PERCENT' in row[0]:
                     records_on_page = row[0][25:]
                if len(row) > 3:
                   if row[0] != 'setup_queries':
                        setup_queries[records_on_page].append(float(row[0]))
                        grouping_queries[records_on_page].append(float(row[1]))
                        individual_guess_queries[records_on_page].append(float(row[2]))
                        ref_scores_db_queries[records_on_page].append(float(row[3]))
                        guess_db_queries[records_on_page].append(float(row[4]))
                        total_db_queries[records_on_page].append(float(row[5]))
                elif len(row) == 3:
                    total_guesses[records_on_page] += 1
                    if int(row[1]) == int(row[2]):
                         total_correct_guesses[records_on_page] += 1
                    #  print(row)
                # # print(row)
                # if 'PERCENT' in row[0]:
                #      print(row)
                #      records_on_page = row[0][25:]
                # if 'NUMBER OF GROUPS' in row[0]:
                #      print('group')
                # elif "individually_tested_groups" in row[0]:
                #      print(row)
                # elif "Total DB Queries This Round:" not in row[0] and 'Total time spent this round in seconds:' not in row[0] and 'ref_score_db_queries' not in row[0] and 'true_label' not in row[0] and 'PERCENT' not in row[0] and 'QUERIES' not in row[0] and 'individual_guess_queries' not in row[0] and 'num_secrets' not in row[0] and 'setup_queries' not in row[0] and records_on_page not in row[0]:
                #     # print(row)
                #     grouping_queries[records_on_page].append(float(row[1]))
                #     individual_guess_queries[records_on_page].append(float(row[2]))
                #     ref_scores_db_queries[records_on_page].append(float(row[3]))
                #     guess_db_queries[records_on_page].append(float(row[4]))
                #     total_db_queries[records_on_page].append(float(row[5]))
                # elif "Total DB Queries This Round:" in row[0]:
                #     total_db_queries[records_on_page].append(int(row[0][28:]))
                # elif "Total time spent this round in seconds:" in row[0]:
                #     total_times[records_on_page].append(float(row[0][39:]))
                # else:
                #     print(row)
                #     if records_on_page != 'num_secrets' and 'PERCENT' not in row[0] and 'QUERIES' not in row[0]:
                #         total_guesses[records_on_page] += 1
                #     if 'PERCENT' not in row[0] and 'QUERIES' not in row[0] and row[int(1)] == row[int(2)]:
                #         total_correct_guesses[records_on_page] +=1
        f = open(filename + ".csv", "a")
        # f.write('case,records on page,accuracy,average time,average number of queries\n')
        f.write(case + '\n')
        f.write('ACCURACIES\n')
        for i in total_guesses:
             accuracy = round(total_correct_guesses[i]/total_guesses[i], 3)
             f.write("("+str(i)+","+str(accuracy)+")")

        # f.write('\nATTACK TIMES\n')
        # for i in total_guesses:
        #     f.write("("+str(i)+","+str(round(statistics.mean(total_times[i]), 3))+")")
        f.write('\nNUMBER OF DB QUERIES FOR SETUP\n')
        for i in total_guesses:
            f.write(str(round(statistics.mean(setup_queries[i]), 3)) + "\n")
        f.write('\nNUMBER OF DB QUERIES FOR GROUPS\n')
        for i in total_guesses:
            f.write("("+str(i)+","+str(round(statistics.mean(grouping_queries[i]), 3))+")")
        f.write('\nNUMBER OF DB QUERIES FOR INDIVIDUAL GUESSES\n')
        for i in total_guesses:
            f.write("("+str(i)+","+str(round(statistics.mean(individual_guess_queries[i]), 3))+")")
        f.write('\nNUMBER OF DB QUERIES FOR REFERENCE SCORES\n')
        for i in total_guesses:
            f.write("("+str(i)+","+str(round(statistics.mean(ref_scores_db_queries[i]), 3))+")")
        f.write('\nNUMBER OF DB QUERIES FOR GUESS SCORES\n')
        for i in total_guesses:
            f.write("("+str(i)+","+str(round(statistics.mean(guess_db_queries[i]), 3))+")")
        f.write('\nNUMBER OF DB QUERIES\n')  
        for i in total_guesses:  
            f.write("("+str(i)+","+str(round(statistics.mean(total_db_queries[i]), 3))+")")
        f.write('\n')

        f.write('\nNUMBER OF DB QUERIES FOR GROUPS\n')
        for i in total_guesses:
            f.write(str(round(statistics.mean(grouping_queries[i]), 3))+"\n")
        f.write('\nNUMBER OF DB QUERIES FOR INDIVIDUAL GUESSES\n')
        for i in total_guesses:
            f.write(str(round(statistics.mean(individual_guess_queries[i]), 3))+"\n")
        f.write('\nNUMBER OF DB QUERIES FOR REFERENCE SCORES\n')
        for i in total_guesses:
            f.write(str(round(statistics.mean(ref_scores_db_queries[i]), 3))+"\n")
        f.write('\nNUMBER OF DB QUERIES FOR GUESS SCORES\n')
        for i in total_guesses:
            f.write(str(round(statistics.mean(guess_db_queries[i]), 3))+"\n")
        f.write('\nNUMBER OF DB QUERIES\n')  
        for i in total_guesses:  
            f.write(str(round(statistics.mean(total_db_queries[i]), 3))+"\n")
        f.write('\n')
        for i in total_guesses:
            f.write(str(total_db_queries[i]))
        # print("Accuracy: " + str(round(total_correct_guesses/total_guesses, 3)))
        # print("Total attack time: " + str(round(total_time, 3)))
        # print("Total DB Queries: " + str(round(total_db_queries, 3)))
        # print(str(round(total_correct_guesses/total_guesses, 3)) + "," + str(round(total_time, 3)) + "," + str(round(total_db_queries, 3)))