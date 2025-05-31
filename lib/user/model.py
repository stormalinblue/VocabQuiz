from typing import Tuple

import sqlite3

from ..common import exceptions

class User(object):
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username

class UserModel(object):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def create_session(self, user_name: str):
        cur = self.connection.cursor()
        users = cur.execute('''
            select users.id, users.user_name from users
            where users.user_name = ? limit 1''',
            (user_name,)).fetchall()
        if len(users) == 0:
            raise exceptions.NotFound
        else:
            user_result: Tuple[int, str] = users[0]
            user_id, username = user_result
            return User(user_id, username)
    
    def create_user(self, user_name: str):
        cur = self.connection.cursor()
        try:
            result = cur.execute('insert into users (user_name) values (?) returning (users.id, users.user_name)', (user_name,)).fetchone()
            self.connection.commit()
            return User(result[0], result[1])
        except:
            raise exceptions.NotModified
    
    def delete_user(self, user_name: str):
        cur = self.connection.cursor()
        try:
            cur.execute('delete from users where users.user_name = ?', (user_name,))
            self.connection.commit()
        except:
            raise exceptions.NotModified
    
    def list_users(self):
        cur = self.connection.cursor()
        result = cur.execute('select (users.user_name) from users order by users.user_name asc')
        return (row[0] for row in result.fetchall())