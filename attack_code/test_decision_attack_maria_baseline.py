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

secrets_to_try = [100]
secrets_to_try.reverse()
for num_secrets in secrets_to_try:
    for trial in range(0, 50):
        random.shuffle(possibilities)
        trial_possibilities = possibilities[0:200]
        success = False
        control.drop_table(table)
        control.create_basic_table(table,
            varchar_len=maxRowSize,
            compressed=True,
            encrypted=True)
        guesses = []
        correct_guesses = set()

        for secret_idx in range(num_secrets):
            secret = trial_possibilities[(trial + secret_idx) % len(trial_possibilities)]
            control.insert_row(table, secret_idx, secret)
            guesses.append(secret)
            correct_guesses.add(secret)

        for secret_idx in range(num_secrets, num_secrets*2):
            wrong_guess = trial_possibilities[(trial + secret_idx) % len(trial_possibilities)]
            guesses.append(wrong_guess)

        fillerCharSet = string.printable.replace(string.ascii_lowercase, '').replace('*', '')
        if sys.argv[1] == "--emails":
            fillerCharSet = fillerCharSet.replace('_', '').replace('.', '').replace('@', '')
        dbreacher = dbreacher_impl.DBREACHerImpl(control, table, num_secrets, maxRowSize, fillerCharSet, ord('*'))
        
        startRound = time.time()

        attacker = decision_attacker.decisionAttacker(dbreacher, guesses)
        while not success:
            setupStart = time.time()
            success = attacker.setUp()
            setupEnd = time.time()
            if success:
                success = attacker.tryAllGuesses()
            end = time.time()
        refScores = attacker.getGuessAndReferenceScores()
        endRound = time.time()
        for guess, score_tuple in refScores:
            label = 1 if guess in correct_guesses else 0
            print(str(label)+","+str(num_secrets)+","+str(score_tuple[0])+","+str(score_tuple[1])+","+str(score_tuple[2]) +","+str(setupEnd - setupStart)+","+str((end-setupEnd)/num_secrets))
        print("ref_score_db_queries,individual_queries,total_queries")
        print(str(dbreacher.db_ref_score_count)+","+str(dbreacher.db_guess_count)+","+str(dbreacher.db_count))
        print("Total DB Queries This Round: " + str(dbreacher.db_count))
        print("Total time spent this round in seconds: " + str(endRound-startRound))
