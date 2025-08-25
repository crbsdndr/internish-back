from datetime import datetime, timezone, timedelta

from internish.security import decode_token, make_access_token, make_refresh_token
from internish.settings import config_jwt

from user_app.utils import user_utils
from user_app.views import user_interact


class AuthService:
    def login(self, email: str, password: str):
        user = user_interact.get_by_email(email=email)
        if not user:
            raise ValueError("User not found")

        if not user_utils.verify_password(password, user["password_hash_"]):
            raise ValueError("Invalid password")

        access = make_access_token(sub=user["email_"], extra={"role": user["role_"]})
        refresh = make_refresh_token(sub=user["email_"], extra={"role": user["role_"]})

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=config_jwt.REFRESH_EXPIRE_MIN)
        user_interact.save_refresh(user["email_"], refresh, expires_at)

        return {"access_token_": access, "refresh_token_": refresh}

    def refresh_access_token(self, refresh_token_: str):
        payload = decode_token(refresh_token_)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")

        sub = payload.get("sub")
        role = payload.get("role")
        rt = user_interact.get_refresh(refresh_token_)
        if not rt:
            raise ValueError("Refresh token is not registered")

        if rt["revoked_"]:
            raise ValueError("Refresh token is revoked")

        if rt["expires_at_"] <= datetime.now(timezone.utc):
            raise ValueError("Refresh token is expired")

        new_access = make_access_token(sub=sub, extra={"role": role})
        return {"access_token_": new_access, "refresh_token_": refresh_token_}

    def logout(self, refresh_token_: str):
        payload = decode_token(refresh_token_)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")

        user_interact.revoke_refresh(refresh_token_)
        return {"message": "Logged out (refresh token revoked)"}

    def logout_all(self, refresh_token_: str):
        payload = decode_token(refresh_token_)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")

        email = payload.get("sub")
        if not email:
            raise ValueError("Token is not valid")

        user_interact.revoke_all_refresh_by_email(email)
        return {"message": "All sessions revoked"}


auth_service = AuthService()

