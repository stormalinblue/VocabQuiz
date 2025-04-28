import sqlite3
import yaml
from datetime import datetime
import pytz

# Load YAML data
with open('db/words2.yaml', 'r') as file:
    data = yaml.safe_load(file)

# Connect to SQLite database
conn = sqlite3.connect('db/words.db')
cursor = conn.cursor()

# Insert data into the database
for entry in data:
    word = entry['word']
    license = entry['license']['name'] if 'license' in entry else None
    
    # Insert word and get the word_id
    cursor.execute("INSERT OR IGNORE INTO words (word) VALUES (?) RETURNING id", (word,))
    word_id = cursor.fetchone()[0] if cursor.rowcount > 0 else cursor.execute("SELECT id FROM words WHERE word = ?", (word,)).fetchone()[0]
    
    if 'meanings' not in entry:
        print('word', word, 'has no definition')
        continue

    # Insert definitions
    for meaning in entry['meanings']:
        # Insert part of speech and get the part_of_speech_id
        part_of_speech = meaning['partOfSpeech']
        cursor.execute("INSERT OR IGNORE INTO parts_of_speech (name) VALUES (?) RETURNING id", (part_of_speech,))
        part_of_speech_id = cursor.fetchone()[0] if cursor.rowcount > 0 else cursor.execute("SELECT id FROM parts_of_speech WHERE name = ?", (part_of_speech,)).fetchone()[0]

        # Insert into word_parts_of_speech
        cursor.execute("INSERT OR IGNORE INTO word_parts_of_speech (word_id, part_of_speech_id) VALUES (?, ?) returning id", (word_id, part_of_speech_id))
        word_pos_id = cursor.fetchone()[0] if cursor.rowcount > 0 else cursor.execute("SELECT id FROM word_parts_of_speech WHERE word_id = ? and part_of_speech_id = ?", (word_id, part_of_speech_id)).fetchone()[0]

        for definition in meaning['definitions']:
            definition_text = definition['definition']
            cursor.execute("INSERT INTO word_definitions (word_pos_id) VALUES (?) RETURNING id", (word_pos_id,))
            definition_id = cursor.fetchone()[0]
            
            # Insert definition revisions
            add_date = int(datetime.now(pytz.utc).timestamp())  # Get current UTC time
            source = entry['sourceUrls'][0] if 'sourceUrls' in entry and len(entry['sourceUrls']) > 0 else None
            cursor.execute("INSERT INTO definition_revisions (definition_id, definition_text, add_date, source, license) VALUES (?, ?, ?, ?, ?)", (definition_id, definition_text, add_date, source, license))

# Commit changes and close the connection
conn.commit()
conn.close()
