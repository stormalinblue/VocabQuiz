import argparse
import sys
import sqlite3

from lib.word.model import WordModel
from lib.game.model import GameModel
from lib.user.model import UserModel

from lib.word.cli_view import WordCLIView
from lib.game.cli_view import GameCLIView
from lib.user.cli_view import UserCLIView


def main(argv):
    db_connection = sqlite3.connect('db/words.db', autocommit=False)
    db_connection.execute('PRAGMA foreign_keys = ON')
    parser = argparse.ArgumentParser(prog='VocabQuiz')

    subparsers = parser.add_subparsers()
    word_cli = WordCLIView(WordModel(db_connection))
    word_cli.add_subparsers(subparsers)

    user_model = UserModel(db_connection)
    game_cli = GameCLIView(GameModel(db_connection), user_model)
    game_cli.add_subparsers(subparsers)

    user_cli = UserCLIView(user_model)
    user_cli.add_subparsers(subparsers)
    args = parser.parse_args(argv)
    if hasattr(args, 'func'):
        args.func(args)
    db_connection.close()

if __name__ == '__main__':
    main(sys.argv[1:])