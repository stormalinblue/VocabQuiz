from ..common import exceptions

class WordCLIView(object):
    def __init__(self, model):
        self.model = model
    
    def add_word(self, args):
        try:
            self.model.add_word(args.new_word)
        except exceptions.NotModified:
            print('We already have this word.')

    def add_subparsers(self, parent_subparsers):
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
    

    