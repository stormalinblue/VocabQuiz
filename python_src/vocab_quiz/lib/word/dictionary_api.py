from typing import Union, Dict, List, TypedDict

import requests

from ..common import exceptions

JsonType = Union[str, int, float, bool, None, Dict[str, 'JsonType'], List['JsonType']]

class Definition(TypedDict):
    definition: str

class Meaning(TypedDict):
    partOfSpeech: str
    sourceUrls: List[str]
    definitions: List[Definition]

class License(TypedDict):
    name: str

class Entry(TypedDict, total=False):
    license: License
    sourceUrls: List[str]
    meanings: List[Meaning]

class DictionaryAPISession(object):
    def __init__(self, session: requests.Session=requests.Session()):
        self.session = session
    
    @staticmethod
    def make_url(word: str):
        return f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'

    def get_definition(self, word: str) -> Entry:
        url = self.make_url(word)
        response = self.session.get(url)
        if response.status_code == 404:
            raise exceptions.NotFound
        elif response.status_code != 200:
            raise exceptions.InternalServerError

        return response.json()[0]