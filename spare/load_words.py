import sqlite3
import time

from lib.word.model import WordModel
from lib.common.util import utc_now_sec_timestamp
from lib.common import exceptions

with open('db/words_batch_2.txt') as words_file:
    words = words_file.read().strip().split()

connection = sqlite3.connect('./db/words.db', autocommit=False)
connection.execute('PRAGMA foreign_keys = ON')
word_model = WordModel(connection)

wait_time_sec = 1

for word in words:
    timestamp = utc_now_sec_timestamp()
    print('adding word', word)
    need_sleep = True
    try:
        word_id = word_model.add_word(word, timestamp)
    except exceptions.NotModified:
        print('word', repr(word), 'already in database')
        need_sleep = False
    except exceptions.NotFound:
        print('word', repr(word), 'not found')
    else:
        print('added word id', word)
    print()
    if need_sleep:
        time.sleep(wait_time_sec)