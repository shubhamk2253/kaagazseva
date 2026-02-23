from models.user import User
from extensions import db

class UserRepository:
    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_phone(phone):
        return User.query.filter_by(phone=phone).first()

    @staticmethod
    def create(phone, role, name=None):
        user = User(phone=phone, role=role, name=name)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_profile(user_id, name):
        user = User.query.get(user_id)
        if user:
            user.name = name
            db.session.commit()
        return user
