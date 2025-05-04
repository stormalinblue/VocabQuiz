from ..common import exceptions

class UserSession(object):
    def __init__(self, user_id):
        self.user_id = user_id

class UserModel(object):
    def __init__(self, connection):
        self.connection = connection
    
    def create_session(self, user_name):
        cur = self.connection.cursor()
        users = cur.execute('select (users.id) from users where users.user_name = ? limit 1', (user_name,)).fetchall()
        if len(users) == 0:
            raise exceptions.NotFound
        else:
            return UserSession(users[0][0])
    
    def create_user(self, user_name):
        cur = self.connection.cursor()
        try:
            result = cur.execute('insert into users (user_name) values (?) returning users.id', (user_name,)).fetchone()
            self.connection.commit()
            return UserSession(result[0])
        except:
            raise exceptions.NotModified
    
    def delete_user(self, user_name):
        cur = self.connection.cursor()
        try:
            result = cur.execute('delete from users where users.user_name = ?', (user_name,))
            self.connection.commit()
        except:
            raise exceptions.NotModified
    
    def list_users(self):
        cur = self.connection.cursor()
        result = cur.execute('select (users.user_name) from users order by users.user_name asc')
        return (row[0] for row in result.fetchall())