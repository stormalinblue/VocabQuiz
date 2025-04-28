import string
import os
import pickle

import numpy as np
import pandas as pd

from matcher import QuestionDB

rng = np.random.default_rng(seed=0)


try:
    with open('performance.pkl', 'rb') as f:
        qdb = pickle.load(f)
    print('loaded')
except FileNotFoundError:
    qdb = QuestionDB('words2.yaml')

try:
    while True:
        pos, ans_id, mcq = qdb.get_mcq(rng, 4)
        promoted_row = mcq.loc[ans_id]
        num_choices = mcq.shape[0]
        # print(mcq)

        mcq['letter'] = list(string.ascii_uppercase[:num_choices])
        print(f'{promoted_row.word} ({promoted_row.partOfSpeech})')
        for _, question_row in mcq.iterrows():
            print(f"{question_row['letter']}) {question_row['definition']}")

        while True:
            ans = input().strip().upper()

            if (mcq['letter'] == ans).any():
                attempted_word_id = attempted_word_row = mcq[mcq['letter'] == ans].index[0]
                qdb.register_mcq_response(pos, ans_id, attempted_word_id, mcq.index)
            if mcq.loc[ans_id]['letter'] == ans:
                print('Correct!')
                for _, question_row in mcq.iterrows():
                    print(f"{question_row['letter']} -> {question_row['word']}")
                print()
                break
            else:
                if (mcq['letter'] == ans).any():
                    attempted_word_row = mcq[mcq['letter'] == ans].iloc[0]
                    print('Incorrect, that is the definition of', attempted_word_row.word)
                else:
                    print('Incorrect, try again.')
finally:
    with open('performance.pkl', 'wb') as f:
        pickle.dump(qdb, f)