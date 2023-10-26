from datetime import datetime
from flask_login import UserMixin


from app import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = 'base_user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
