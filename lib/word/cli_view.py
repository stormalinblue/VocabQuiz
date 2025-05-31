from typing import cast, Any, Union

import argparse

from ..common import exceptions
from ..common.util import utc_now_sec_timestamp

from .model import WordModel

class WordCLIView(object):
    def __init__(self, model: WordModel):
        self.model = model
    
    def add_word(self, args: Any) -> None:
        now = utc_now_sec_timestamp()
        try:
            word: str = cast(str, args.new_word)
            self.model.add_word(word, now)
        except exceptions.NotModified:
            print('We already have this word.')
    
    def search_words(self, args: Any) -> None:
        prefix: str = cast(str, args.prefix)
        results = self.model.word_search(prefix)
        for word in results:
            print(word)
    
    def _print_word_details(self, word: str) -> None:
        detail = self.model.word_detail(word)

        print(f'({detail["id"]}) {detail["word"]}')
        for definition in detail['definitions']:
            print(definition['pos'], definition['defn_id'], definition['definition_text'])

    
    def detail_word(self, args: Any) -> None:
        word: str = cast(str, args.word)
        try:
            self._print_word_details(word)
        except exceptions.NotFound:
            print('Could not find a definition for', word)
    
    def edit_word(self, args: Any) -> None:
        word: str = cast(str, args.word)
        try:
            self._print_word_details(word)
        except exceptions.NotFound:
            print('Word', repr(word), 'not found.')
        else:
            valid_definition_id = False
            user_definition_id: Union[int, None] = None
            while not valid_definition_id:
                user_input = input('Enter definition id to edit: ')
                try:
                    user_definition_id = int(user_input)
                except ValueError:
                    print('Invalid definition id.')
                else:
                    if not self.model.word_has_definition(word, user_definition_id):
                        print(f'No definition id {user_definition_id} for word {word}')
                    else:
                        valid_definition_id = True

            print('Enter new definition.')
            user_definition = input()
            
            self.model.revise_definition(cast(int, user_definition_id), user_definition, utc_now_sec_timestamp())

    def add_subparsers(self, parent_subparsers: Any) -> None:
        word_parser = parent_subparsers.add_parser(
            'word',
            help='CRUD words')
        word_subparsers = word_parser.add_subparsers()
        
        add_parser = word_subparsers.add_parser(
            'add',
            help='Add a new word to the dictionary.')
        add_parser.add_argument(
            'new_word',
            type=str,
            help='The new word to add.')
        add_parser.set_defaults(func=self.add_word)

        search_parser = word_subparsers.add_parser(
            'search',
            help='Search all words by prefix'
        )
        search_parser.add_argument(
            'prefix',
            type=str,
            help='The prefix to search by.'
        )
        search_parser.set_defaults(func=self.search_words)

        detail_parser = word_subparsers.add_parser(
            'detail',
            help='Get the details about a word',
        )
        detail_parser.add_argument(
            'word',
            type=str,
            help='The word to detail.'
        )
        detail_parser.set_defaults(func=self.detail_word)

        edit_parser = word_subparsers.add_parser(
            'edit',
            help='Edit the definitions of a word'
        )
        edit_parser.add_argument(
            'word',
            type=str,
            help='The word to edit.'
        )
        edit_parser.set_defaults(func=self.edit_word)
    

    