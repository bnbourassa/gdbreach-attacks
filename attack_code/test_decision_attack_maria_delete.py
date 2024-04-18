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

print("true_label,num_secrets,b_no,b_guess,b_yes,setup_time,per_guess_time")

secrets_to_try = [1, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
secrets_to_try.reverse()
for num_secrets in secrets_to_try:
    random.shuffle(possibilities)
    for trial in range(0, 200, num_secrets):
        startRound = time.time()
        success = False
        control.drop_table(table)
        control.create_basic_table(table,
            varchar_len=maxRowSize,
            compressed=True,
            encrypted=True)
        guesses = []
        correct_guesses = set()


        for secret_idx in range(num_secrets):
            secret = possibilities[(trial + secret_idx) % len(possibilities)]
            control.insert_row(table, secret_idx, secret)
            guesses.append(secret)
            correct_guesses.add(secret)

        for secret_idx in range(num_secrets, num_secrets*2):
            wrong_guess = possibilities[(trial + secret_idx) % len(possibilities)]
            guesses.append(wrong_guess)


        fillerCharSet = string.printable.replace(string.ascii_lowercase, '').replace('*', '')
        if sys.argv[1] == "--emails":
            fillerCharSet = fillerCharSet.replace('_', '').replace('.', '').replace('@', '')
        dbreacher = dbreacher_impl.DBREACHerImpl(control, table, i, maxRowSize, fillerCharSet, ord('*'))

        fifty_percent = len(correct_guesses)//2
        deleted_indices = []
        for i in range(fifty_percent):
            index = random.randint(0, len(correct_guesses)-1)
            while index in deleted_indices:
                index = random.randint(0, len(correct_guesses)-1)
            deleted_indices.append(index)
            control.delete_guess(table, list(correct_guesses)[index])
        
        startRound = time.time()

        attacker = decision_attacker.decisionAttacker(dbreacher, guesses)
        while not success:
            curr_db_count = dbreacher.db_count
            setupStart = time.time()
            success = attacker.setUp()
            setupEnd = time.time()
            dbreacher.db_setup_count += dbreacher.db_count - curr_db_count
            curr_db_count = dbreacher.db_count
            if success:
                success = attacker.tryAllGuesses()
            end = time.time()
            dbreacher.db_individual_guess_count += (dbreacher.db_count - curr_db_count)
        refScores = attacker.getGuessAndReferenceScores()
        endRound = time.time()
        for guess, score_tuple in refScores:
            label = 1 if guess in correct_guesses else 0
            print(str(label)+","+str(i)+","+str(score_tuple[0])+","+str(score_tuple[1])+","+str(score_tuple[2]) +","+str(setupEnd - setupStart)+","+str((end-setupEnd)/i))
        print("setup_queries,individual_guess_queries,reference_score_queries,guess_score_queries,total_queries")
        print(str(dbreacher.db_setup_count) + "," + str(dbreacher.db_individual_guess_count)+","+str(dbreacher.db_ref_score_count)+","+str(dbreacher.db_guess_count)+","+str(dbreacher.db_count))
        print("Total time spent this round in seconds: " + str(endRound-startRound))
