## Grouped Attack Setup
import utils.mariadb_utils as utils
import dbreacher
import dbreacher_impl
import decision_attacker
import random
import string
import time
import sys
import numpy as np

maxRowSize = 200

control = utils.MariaDBController("testdb")

table = "victimtable"
control.drop_table(table)
control.create_basic_table(table,
            varchar_len=maxRowSize,
        compressed=True,
        encrypted=True)

possibilities = []
if sys.argv[1] == "--random":
    for _ in range(2000):
        size = np.random.randint(10, 20)
        secret = "".join(random.choices(string.ascii_lowercase, k=size))
        possibilities.append(secret)
if sys.argv[1] == "--english":
    with open("/home/bnboura/dbreach-britney/resources/10000-english-long.txt") as f:
        for line in f:
            word = line.strip().lower()
            possibilities.append(word)
if sys.argv[1] == "--emails":
    with open("/home/bnboura/dbreach-britney/resources/fake-emails.txt") as f:
        for line in f:
            email = line.strip().lower()
            possibilities.append(email)

# print("true_label,num_secrets,b_no,b_guess,b_yes,setup_time,per_guess_time,attack_guess")
print("num_secrets,true_label,guess_label")



def runDecisionAttack(num_secrets, setupEnd, setupStart, attacker, guesses, correct_guesses):
    attacker.bytesShrunk = dict()
    attacker.bYesReferenceScores = dict()
    attacker.bNoReferenceScores = dict()
    attacker.tryGroupedGuesses(guesses)
    refScores = attacker.getGuessAndReferenceScores()
    new_trials = []
    for guess, score_tuple in refScores:
            label = 0
            if guess in correct_guesses:
                label = 1
            new_trials.append([label, num_secrets, score_tuple[0], score_tuple[1], score_tuple[2], setupEnd - setupStart, (end-setupEnd)/num_secrets])
    
    # initial finding of ones that are true
    true_labels = []
    ref_scores = []
    setup_times = []
    guess_times = []
    for trial in new_trials:
        if(trial[0] == 0 or trial[0] == 1):
            true_labels.append(int(trial[0]))
            ref_scores.append((int(trial[2]) if trial[2] != 0 else 1, int(trial[3]), int(trial[4])))
        else:
            pass
        setup_times.append(float(trial[5]))
        guess_times.append(float(trial[6]))
    true_labels = np.array(true_labels)
    pcts = [1 - (b - b_yes) / b_no for b_no, b, b_yes in ref_scores]
    threshold = 0.60

    guess_index = 0
    trial_index = 0
    for pct in pcts:
        if pct >= threshold:
            print(str(num_secrets)+","+str(new_trials[trial_index][0])+",1")
        else:
            print(str(num_secrets)+","+str(new_trials[trial_index][0])+",0")
        guess_index += 1
        trial_index += 1

def outputWrongGuesses(num_secrets, setupEnd, setupStart, attacker, guesses, trial_index, trials):
    current_trial = trials[trial_index]
    for guess in guesses:
        label = 1 if guess in correct_guesses else 0
        print(str(num_secrets)+","+str(label)+",0")


#secrets_to_try = [1, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
# secrets_to_try = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
# secrets_to_try = [1, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
secrets_to_try = [1, 20, 40, 60, 80, 100, 120]
secrets_to_try.reverse()
for num_secrets in secrets_to_try:
    #random.shuffle(possibilities)
    fullAttackStart = time.time()
    for trial in range(0, 200, num_secrets):
    # for trial in range(0, 20, num_secrets):
        success = False
        control.drop_table(table)
        control.create_basic_table(table,
            varchar_len=maxRowSize,
            compressed=True,
            encrypted=True)
        guesses = []
        guesses_grouped = []
        word_groups = {}
        correct_guesses = set()
        correct_guesses_grouped = set()
        group_count = 1
        group_word = ''
        # for secret_idx in range(num_secrets):
        # five_percent_of_secrets = (num_secrets * 5) // 100
        # one_percent_of_secrets = (num_secrets * 1) // 100
        # ten_percent_of_secrets = (num_secrets * 10) // 100
        # twenty_percent_of_secrets = (num_secrets * 20) // 100
        # thirty_percent_of_secrets = (num_secrets * 30) // 100
        # fifty_percent_of_secrets = (num_secrets * 50 // 100)
        # twenty_five_percent_of_secrets = (num_secrets * 25) // 100
        for secret_idx in range(num_secrets):
            secret = possibilities[(trial + secret_idx) % len(possibilities)]
            control.insert_row(table, secret_idx, secret)
            guesses.append(secret)
            correct_guesses.add(secret)

        for secret_idx in range(num_secrets, num_secrets*2):
            wrong_guess = possibilities[(trial + secret_idx) % len(possibilities)]
            guesses.append(wrong_guess)


        random.shuffle(guesses)
        # random.shuffle(guesses)
        group_count = 1
        group_word = ''
        group_words = []
        for guess in guesses:
            if group_count < 3:
                group_word += guess
                group_count += 1
                group_words.append(guess)
            else:
                group_word += guess
                group_words.append(guess)
                guesses_grouped.append(group_word)
                word_groups[group_word] = group_words
                group_count = 1
                group_word = ''
                group_words = []

        fillerCharSet = string.printable.replace(string.ascii_lowercase, '').replace('*', '')
        if sys.argv[1] == "--emails":
            fillerCharSet = fillerCharSet.replace('_', '').replace('.', '').replace('@', '')
        dbreacher = dbreacher_impl.DBREACHerImpl(control, table, num_secrets, maxRowSize, fillerCharSet, ord('*'))

        # attacker = decision_attacker.decisionAttacker(dbreacher, guesses)
        attacker = decision_attacker.decisionAttacker(dbreacher, guesses)
        while not success:
            setupStart = time.time()
            success = attacker.setUp()
            setupEnd = time.time()
            if success:
                success = attacker.tryGroupedGuesses(guesses_grouped)
                # success = attacker.tryAllGuesses()
            end = time.time()
        refScores = attacker.getGuessAndReferenceScores()

        trials = []
        for guess, score_tuple in refScores:
            # print(guess)
            in_group = 0
            for word in word_groups[guess]:
                if word in correct_guesses:
                    in_group = 1
                    break
            label = in_group 
            trials.append([label, num_secrets, score_tuple[0], score_tuple[1], score_tuple[2], setupEnd - setupStart, (end-setupEnd)/num_secrets])

        # initial finding of ones that are true
        true_labels = []
        ref_scores = []
        setup_times = []
        guess_times = []
        for trial in trials:
            if(trial[0] == 0 or trial[0] == 1):
                true_labels.append(int(trial[0]))
                ref_scores.append((int(trial[2]) if trial[2] != 0 else 1, int(trial[3]), int(trial[4])))
            else:
                pass
                #print(trial)
            setup_times.append(float(trial[5]))
            guess_times.append(float(trial[6]))
        true_labels = np.array(true_labels)
        pcts = [1 - (b - b_yes) / b_no for b_no, b, b_yes in ref_scores]
        # print(pcts)

        # no shuffle threshold
        # threshold = 0.64

        # shuffle threshold
        threshold = 0.39

        guess_index = 0
        trial_index = 0
        for pct in pcts:
            if pct >= threshold:
                runDecisionAttack(num_secrets, setupEnd, setupStart, attacker, word_groups[guesses_grouped[guess_index]], correct_guesses)
            else:
                outputWrongGuesses(num_secrets, setupEnd, setupStart, attacker, word_groups[guesses_grouped[guess_index]], trial_index, trials)
            guess_index += 1
            trial_index += 1
    fullAttackEnd = time.time()
    print("Total attack time: " + str(fullAttackEnd-fullAttackStart))





## Old Attack Setup

# import utils.mariadb_utils as utils
# import dbreacher
# import dbreacher_impl
# import decision_attacker
# import random
# import string
# import time
# import sys

# maxRowSize = 200

# control = utils.MariaDBController("testdb")

# table = "victimtable"
# control.drop_table(table)
# control.create_basic_table(table,
#             varchar_len=maxRowSize,
#         compressed=True,
#         encrypted=True)

# #print("Reading in all guesses... \n")
# possibilities = []
# if sys.argv[1] == "--random":
#     for _ in range(2000):
#         size = np.random.randint(10, 20)
#         secret = "".join(random.choices(string.ascii_lowercase, k=size))
#         possibilities.append(secret)
# if sys.argv[1] == "--english":
#     # with open("/home/bnboura/dbreach-britney/resources/10000-english-long.txt") as f:
#     with open("/home/bnboura/dbreach-britney/resources/english-mixed-length-fixed-dataset.txt") as f:
#         for line in f:
#             word = line.strip().lower()
#             possibilities.append(word)
# if sys.argv[1] == "--emails":
#     with open("/home/bnboura/dbreach-britney/resources/fake-emails.txt") as f:
#         for line in f:
#             email = line.strip().lower()
#             possibilities.append(email)

# # random.shuffle(possibilities);

# # f = open("/home/bnboura/dbreach-britney/resources/10000-english-mixed-length.txt", "w")
# # for item in possibilities:
# #     f.write(item+"\n")
# # f.close()

# '''
# np.random.shuffle(possibilities)
# for idx, s in enumerate(possibilities):
#     old_size = control.get_table_size(table)
#     control.insert_row(table, idx, s)
#     new_size = control.get_table_size(table)
#     if old_size < new_size:
#         print("Table grew after " + str(idx + 1) + " insertions")
#         assert(False)
# '''
# print("true_label,num_secrets,b_no,b_guess,b_yes,setup_time,per_guess_time")

# # secrets_to_try = [1, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
# secrets_to_try = [1, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
# # secrets_to_try = [20]
# secrets_to_try.reverse()
# for num_secrets in secrets_to_try:
#     # random.shuffle(possibilities)
#     fullAttackStart = time.time()
#     for trial in range(0, 200, num_secrets):
#         success = False
#         control.drop_table(table)
#         control.create_basic_table(table,
#             varchar_len=maxRowSize,
#             compressed=True,
#             encrypted=True)
#         guesses = []
#         correct_guesses = set()

#         one_percent_of_secrets = (num_secrets * 1) // 100
#         five_percent_of_secrets = (num_secrets * 5) // 100
#         ten_percent_of_secrets = (num_secrets * 10) // 100
#         twenty_percent_of_secrets = (num_secrets * 20) // 100
#         twenty_five_percent_of_secrets = (num_secrets * 25) // 100

#         for secret_idx in range(twenty_five_percent_of_secrets):
#             secret = possibilities[(trial + secret_idx) % len(possibilities)]
#             control.insert_row(table, secret_idx, secret)
#             guesses.append(secret)
#             correct_guesses.add(secret)
        
#         for secret_idx in range(twenty_five_percent_of_secrets, num_secrets*2):
#             wrong_guess = possibilities[(trial + secret_idx) % len(possibilities)]
#             guesses.append(wrong_guess)

#         fillerCharSet = string.printable.replace(string.ascii_lowercase, '').replace('*', '')
#         if sys.argv[1] == "--emails":
#             fillerCharSet = fillerCharSet.replace('_', '').replace('.', '').replace('@', '')
#         dbreacher = dbreacher_impl.DBREACHerImpl(control, table, num_secrets, maxRowSize, fillerCharSet, ord('*'))
        
# #        for guess in correct_guesses:
#  #           control.delete_guess(table, guess)
        
# #        for i in range(len(correct_guesses)//4):
#  #            control.delete_guess(table, list(correct_guesses)[i])
        
#         # control.delete_guess(table, list(correct_guesses)[0])

#         attacker = decision_attacker.decisionAttacker(dbreacher, guesses)
#         while not success:
#             #print("Setting up trial " + str(trial))
#             #control.drop_table(table)
#             #control.create_basic_table(table,
#             #    varchar_len=maxRowSize,
#             #    compressed=True,
#             #    encrypted=True)
#             '''
#             guesses = []
#             correct_guesses = set()
#             for secret_idx in range(num_secrets):
#                 secret = possibilities[(trial + secret_idx) % len(possibilities)]
#                 control.insert_row(table, secret_idx, secret)
#                 guesses.append(secret)
#                 correct_guesses.add(secret)
        
#             for secret_idx in range(num_secrets, num_secrets*2):
#                 wrong_guess = possibilities[(trial + secret_idx) % len(possibilities)]
#                 guesses.append(wrong_guess)

#             dbreacher = dbreacher_impl.DBREACHerImpl(control, table, num_secrets, maxRowSize, string.ascii_uppercase, ord('*'))

#             attacker = decision_attacker.decisionAttacker(dbreacher, guesses)
#             '''
#             setupStart = time.time()
#             success = attacker.setUp()
#             setupEnd = time.time()
#             if success:
#                 success = attacker.tryAllGuesses()
#             end = time.time()
#         #print("Setup succeeded")
#         refScores = attacker.getGuessAndReferenceScores()
#         for guess, score_tuple in refScores:
#             label = 1 if guess in correct_guesses else 0
#             print(str(label)+","+str(num_secrets)+","+str(score_tuple[0])+","+str(score_tuple[1])+","+str(score_tuple[2]) +","+str(setupEnd - setupStart)+","+str((end-setupEnd)/num_secrets))
#     fullAttackEnd = time.time()
#     print("Total attack time: " + str(fullAttackEnd-fullAttackStart))

