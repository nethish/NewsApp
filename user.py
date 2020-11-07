from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, email, name, picture):
        self.email = email
        self.name = name
        self.picture = picture

    def get_id(self):
        return self.email
