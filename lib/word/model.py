from typing import List, Union, Tuple, TypedDict
import sqlite3

from ..common import exceptions

from .dictionary_api import DictionaryAPISession

class POSDefinition(TypedDict):
    defn_id: int
    pos: str
    definition_text: str

class WordDetail(TypedDict):
    id: int
    word: str
    definitions: List[POSDefinition]

class WordModel(object):
    def __init__(self, connection: sqlite3.Connection, session: DictionaryAPISession=DictionaryAPISession()):
        self.connection = connection
        self.dictionary_api_session = session
    
    def word_exists(self, word: str) -> bool:
        result = self.connection.cursor().execute(
            'select count(*) from (select id from words where words.word = ? limit 1)', (word,))
        return result.fetchone()[0] > 0

    def word_search(self, search_str: str) -> List[str]:
        results: List[str] = []
        for result in self.connection.execute('select word from words order by word asc'):
            word = result[0]
            if word.startswith(search_str):
                results.append(word)
        return results

    def word_detail(self, word: str) -> WordDetail:
        cursor = self.connection.cursor()
        word_id_results = cursor.execute('''
            select id from words where words.word = (?)
            ''', (word,)).fetchall()
        
        if not word_id_results:
            raise exceptions.NotFound
    
        word_id: int = word_id_results[0][0]

        pos_definitions: List[Tuple[int, str, str]] = cursor.execute('''
            select ld.definition_id, pos.name, ld.definition_text
            from latest_definitions as ld
            join word_parts_of_speech as word_pos
                on ld.word_pos_id = word_pos.id
            join parts_of_speech as pos
                on word_pos.part_of_speech_id = pos.id
                where word_pos.word_id = ?
            ''', (word_id,)).fetchall()

        return {
            'id': word_id,
            'word': word,
            'definitions': [
                {
                    'defn_id': defn[0],
                    'pos': defn[1],
                    'definition_text': defn[2]}
                for defn in pos_definitions]}

    def word_has_definition(self, word: str, definition_id: int):
        return self.connection.execute('''
            select exists (
                select 1 from word_definitions as wd
                join word_parts_of_speech as word_pos
                    on word_pos.id = wd.word_pos_id
                join words as w
                    on w.id = word_pos.word_id
                where word = (:word) and wd.id = (:definition_id)
            );''',
            {'word': word, 'definition_id': definition_id}).fetchone()[0] == 1

    def revise_definition(self, definition_id: int, new_text: str, timestamp: int) -> None:
        with self.connection:
            self.connection.execute('''
            insert into definition_revisions
            (source, definition_id, definition_text, add_date)
            values ("manual", :definition_id, :definition_text, :add_date)
            ''', {'definition_id': definition_id, 'definition_text': new_text, 'add_date': timestamp})
        

    def add_word(self, new_word: str, add_date: int) -> int:
        if self.word_exists(new_word):
            raise exceptions.NotModified
        try:
            entry = self.dictionary_api_session.get_definition(new_word)
            # print(entry)
            license: Union[str, None] = entry['license']['name'] if 'license' in entry else None 
            if 'sourceUrls' in entry:
                sourceUrls: List[str] = entry['sourceUrls']
                if sourceUrls:
                    source = sourceUrls[0]
                else:
                    source = None
            else:
                source = None

            if 'meanings' not in entry:
                raise Exception(f'Word {new_word} has no definition.')

            with self.connection:
                cursor = self.connection.cursor()

                word_id: int = cursor.execute('''
                    insert into words (word) values (:word)
                    returning id;
                ''', {'word': new_word}).fetchone()[0]

                for meaning in entry['meanings']:
                    part_of_speech: str = meaning['partOfSpeech']

                    pos_exists = cursor.execute('''
                        select exists (select 1 from parts_of_speech as pos
                        where pos.name = (:name))''',
                        {'name': part_of_speech}).fetchone()[0] == 1
                    if pos_exists:
                        pos_id: int = cursor.execute('''
                            select id from parts_of_speech as pos
                            where pos.name = (:name);''',
                            {'name': part_of_speech}).fetchone()[0]
                    else:
                        pos_id: int = cursor.execute(''' 
                            insert into parts_of_speech (name) values (:name)
                            returning parts_of_speech.id as id;''',
                            {'name': part_of_speech}).fetchone()[0]
                
                    word_pos_params = {'word_id': word_id, 'pos_id': pos_id}
                    word_pos_exists = cursor.execute('''
                        select exists (select 1 from word_parts_of_speech as word_pos
                        where word_pos.word_id = (:word_id)
                        and word_pos.part_of_speech_id = (:pos_id));''',
                        word_pos_params).fetchone()[0] == 1
                    if word_pos_exists:
                        word_pos_id: int = cursor.execute('''
                            select word_pos.id from word_parts_of_speech as word_pos
                            where word_pos.word_id = (:word_id)
                            and word_pos.part_of_speech_id = (:pos_id)''',
                            word_pos_params).fetchone()[0]
                    else:
                        word_pos_id: int = cursor.execute('''
                            insert into word_parts_of_speech (word_id, part_of_speech_id)
                            values (:word_id, :pos_id)
                            returning id;''',
                            word_pos_params).fetchone()[0]
                            

                    for definition in meaning['definitions']:
                        definition_text: str = definition['definition']
                      
                        definition_id: int = cursor.execute('''
                            insert into word_definitions (word_pos_id)
                            values (:word_pos_id)
                            returning id;
                            ''', {'word_pos_id': word_pos_id}).fetchone()[0]
                        
                        cursor.execute('''
                            insert into definition_revisions
                            (definition_id, definition_text, add_date, source, license)
                            values (:definition_id, :definition_text, :add_date, :source, :license);''',
                            {
                                'definition_id': definition_id,
                                'definition_text': definition_text,
                                'add_date': add_date,
                                'source': source,
                                'license': license
                            })
                return word_id
                
        finally:
            pass