class UserCLIView(object):
    def __init__(self, model):
        self.model = model
    
    def create_user(self, args):
        self.model.create_user(args.new_user_name)
        print('User', args.new_user_name, 'created!')
    
    def delete_user(self, args):
        self.model.delete_user(args.user_name)
        print('User', args.user_name, 'deleted!')
    
    def list_users(self, args):
        for user_name in self.model.list_users():
            print(user_name)
    
    def add_subparsers(self, parent_subparsers):
        user_parser = parent_subparsers.add_parser(
            'user',
            help='CRUD users')
        user_subparsers = user_parser.add_subparsers()
        
        add_parser = user_subparsers.add_parser(
            'add',
            help='Add a new user.')
        add_parser.add_argument(
            'new_user_name',
            type=str,
            help='The new username to add.')
        add_parser.set_defaults(func=self.create_user)
    
        delete_parser = user_subparsers.add_parser(
            'delete',
            help='Delete a user.')
        delete_parser.add_argument(
            'user_name',
            type=str,
            help='The username to delete.')
        delete_parser.set_defaults(func=self.delete_user)
    
        list_parser = user_subparsers.add_parser(
            'list',
            help='List all users.')
        list_parser.set_defaults(func=self.list_users)