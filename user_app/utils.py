import bcrypt

class UserUtils():
    def password_hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        cleaned_hash = hashed.strip()
        return bcrypt.checkpw(password.encode('utf-8'), cleaned_hash.encode('utf-8'))

user_utils = UserUtils()