from typing import Dict, cast, Any

import string

import pandas as pd

from ..common import exceptions
from ..common.util import utc_now_sec_timestamp

from ..user.model import UserModel
from ..game.model import GameModel

class GameCLIView(object):
    def __init__(self, game_model: GameModel, user_model: UserModel):
        self.game_model = game_model
        self.user_model = user_model
    
    def play_game(self, args) -> None:
        username: str = cast(str, args.username)

        try:
            user = self.user_model.create_session(username)
        except exceptions.NotFound:
            print('User not found')
            exit(1)

        print('Playing as', user.username)
        print()

        try:
            while True:
                print('getting new question')
                presentation_id = self.game_model.create_question(user, utc_now_sec_timestamp())
                print('got question')

                presentation = self.game_model.get_presentation_info(user, presentation_id)
                question = presentation['question']
                word: str = question['word']
                part_of_speech: str = question['part_of_speech']
                options: pd.DataFrame = presentation['options']
                letter_index: Dict[str, int] = dict(zip(string.ascii_uppercase, options.index))

                print(f'{word} ({part_of_speech})')

                letters = list(sorted(letter_index.keys()))
                for letter in letters:
                    option = options.loc[letter_index[letter]]
                    print(f'{letter}) {option.text}')

                while True:
                    print('waiting for answer')
                    user_input = input().strip().upper()
                    if user_input not in letter_index:
                        print('Incorrect. Try again.')
                    else:
                        input_index = letter_index[user_input]
                        is_correct: bool = self.game_model.is_correct_answer(user, presentation_id, input_index)
                        if not is_correct:
                            print('Incorrect. That is the definition of', options.loc[letter_index[user_input]].word)
                        else:
                            print('Correct!')
                            for letter, index in sorted(letter_index.items()):
                                print(f'{letter} -> {options.loc[index].word}')

                        self.game_model.create_user_response(
                            user,
                            presentation_id,
                            [input_index])
                        
                        if is_correct:
                            break
                        else:
                            presentation_id = self.game_model.re_presentation(user, presentation_id, utc_now_sec_timestamp())
                print()
        except KeyboardInterrupt as e:
            print('Goodbye!')
            raise e


    def add_subparsers(self, parent_subparsers: Any) -> None:
        game_parser = parent_subparsers.add_parser(
            'game', help='Play the game')
        game_subparsers = game_parser.add_subparsers()
        
        play_parser = game_subparsers.add_parser(
            'play',
            help='Play the vocab quiz game.')
        play_parser.add_argument(
            'username',
            type=str,
            help='The user name to use for the game.')
        play_parser.set_defaults(func=self.play_game)