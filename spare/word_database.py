import yaml
import pandas as pd

def parse_definition_table(word_responses):
    rows = []
    for word_response in word_responses:
        word = word_response['word']
        if 'meanings' not in word_response:
            print(word, 'missing a definition')
        else:
            meanings = word_response['meanings']
            for meaning in meanings:
                partOfSpeech = meaning['partOfSpeech']
                for definition in (d['definition'] for d in meaning['definitions']):
                    rows.append((partOfSpeech, word, definition))

    return pd.DataFrame(rows, columns=['partOfSpeech', 'word', 'definition'])

def load_definition_table(file_name):
    with open(file_name) as f:
        word_responses = yaml.load(f, yaml.CSafeLoader)
    return parse_definition_table(word_responses)