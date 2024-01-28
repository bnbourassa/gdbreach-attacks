## Grouped Attack Setup
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
    for _ in range(2000):
        size = np.random.randint(10, 20)
        secret = "".join(random.choices(string.ascii_lowercase, k=size))
        possibilities.append(secret)
if sys.argv[1] == "--english":
    with open("./resources/10000-english-long.txt") as f:
        for line in f:
            word = line.strip().lower()
            possibilities.append(word)
if sys.argv[1] == "--emails":
    with open("./resources/fake-emails.txt") as f:
        for line in f:
            email = line.strip().lower()
            possibilities.append(email)

# print("true_label,num_secrets,b_no,b_guess,b_yes,setup_time,per_guess_time,attack_guess")
print("num_secrets,true_label,guess_label")

#secrets_to_try = [1, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
# secrets_to_try = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
secrets_to_try = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
secrets_to_try.reverse()
startAttack = time.time()
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
        guesses_grouped = []
        word_groups = {}
        correct_guesses = set()
        correct_guesses_grouped = set()
        group_count = 1
        group_word = ''
        # for secret_idx in range(num_secrets):
        # five_percent_of_secrets = (num_secrets * 5) // 100
        one_percent_of_secrets = (num_secrets * 1) // 100
        # ten_percent_of_secrets = (num_secrets * 10) // 100
        # twenty_percent_of_secrets = (num_secrets * 20) // 100
        # thirty_percent_of_secrets = (num_secrets * 30) // 100
        # fifty_percent_of_secrets = (num_secrets * 50 // 100)
        # twenty_five_percent_of_secrets = (num_secrets * 25) // 100
        for secret_idx in range(0, one_percent_of_secrets):
            secret = possibilities[(trial + secret_idx) % len(possibilities)]
            control.insert_row(table, secret_idx, secret)
            guesses.append(secret)
            correct_guesses.add(secret)

        for secret_idx in range(one_percent_of_secrets, num_secrets*2):
            wrong_guess = possibilities[(trial + secret_idx) % len(possibilities)]
            guesses.append(wrong_guess)


        random.shuffle(guesses)
        for guess in guesses:
            if guess in correct_guesses:
                print(str(num_secrets)+",1,0")
            else:
                print(str(num_secrets)+",0,0")
        # random.shuffle(guesses)
        group_count = 1