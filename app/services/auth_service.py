from app.models import User
from app.utils.auth import generate_token


class AuthService:
    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return None
        token = generate_token(user)
        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "store_id": user.store_id,
            },
        }
