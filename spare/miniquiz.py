import string

import numpy as np
import pandas as pd

from word_database import load_definition_table

definition_table = load_definition_table('words2.yaml')
part_of_speech_groups = definition_table.groupby('partOfSpeech')
group_sizes = part_of_speech_groups.size()
parts_of_speech = group_sizes.index
parts_of_speech_probabilities = group_sizes / group_sizes.sum()
rng = np.random.default_rng()

while True:
    selected_part_of_speech = rng.choice(group_sizes.index, 1, False, parts_of_speech_probabilities)[0]
    pos_rows = part_of_speech_groups.get_group(selected_part_of_speech)
    promoted_row_index = rng.choice(pos_rows.index, 1, False)[0]
    promoted_row = pos_rows.loc[promoted_row_index]

    alternative_definitions = pos_rows[pos_rows.word != promoted_row.word]
    num_choices = min(3, alternative_definitions.shape[0])
    alternative_choice_index = rng.choice(alternative_definitions.index, num_choices, False)
    mcq_row_indices = np.concat([alternative_choice_index, [promoted_row_index]])
    rng.shuffle(mcq_row_indices)

    mcq = pos_rows.loc[mcq_row_indices]
    mcq['letter'] = list(string.ascii_uppercase[:num_choices + 1])
    print(f'{promoted_row.word} ({promoted_row.partOfSpeech})')
    for _, question_row in mcq.iterrows():
        print(f"{question_row['letter']}) {question_row['definition']}")


    with open('ans_log.csv', 'a') as out_file:
        while True:
            ans = input().strip().upper()

            if mcq.loc[promoted_row_index]['letter'] == ans:
                print('Correct!')
                for _, question_row in mcq.iterrows():
                    print(f"{question_row['letter']} -> {question_row['word']}")
                print()
                out_file.write(','.join([selected_part_of_speech, promoted_row.word, promoted_row.word]) + '\n')
                break
            else:
                if (mcq['letter'] == ans).any():
                    attempted_word_row = mcq[mcq['letter'] == ans].iloc[0]
                    print('Incorrect, that is the definition of', attempted_word_row.word)
                    out_file.write(','.join([selected_part_of_speech, promoted_row.word, attempted_word_row.word]) + '\n')
                else:
                    print('Incorrect, try again.')
