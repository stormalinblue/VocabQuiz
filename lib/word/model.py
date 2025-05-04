import requests

from ..common import exceptions

class DictionaryAPISession(object):
    def __init__(self, session=requests.Session()):
        self.session = session
    
    @staticmethod
    def make_url(word):
        return f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'

    def get_definition(self, word):
        url = self.make_url(word)
        response = self.session.get(url)
        if response.status_code == 404:
            raise exceptions.NotFound
        elif response.status_code != 200:
            raise exceptions.InternalServerError

        return response.json()

class WordModel(object):
    def __init__(self, connection, session=DictionaryAPISession()):
        self.connection = connection
        self.dictionary_api_session = session
    
    def word_exists(self, word):
        result = self.connection.cursor().execute(
            'select (words.id) from words where words.word = ? limit 1', (word,))
        return len(result.fetchall()) > 0

    def add_word(self, new_word):
        print('adding', new_word)

        if self.word_exists(new_word):
            raise exceptions.NotModified

        try:
            definition = self.dictionary_api_session.get_definition(new_word)
            print(definition)
        finally:
            pass