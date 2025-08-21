import token
from internish import connect
from user_app import serializers

class UserInteract(connect.PostgresConnection):
    def list(self):
        query = "SELECT * FROM users"
        return self.fetchall(query)

    def index(self, id=None, email=None):
        if (id is not None) and (email is not None):
            raise ValueError("Provide only one parameter: either 'id' or 'email', not both.")

        if (id is None) and (email is None):
            raise ValueError("You must provide either 'id' or 'email'.")

        if id is not None:
            query = "SELECT * FROM users WHERE user_id = %s"
            return self.fetchone(query, (id,))

        else:
            query = "SELECT * FROM users WHERE email_ = %s"
            return self.fetchone(query, (email,))

    def create(self, item):
        query = """INSERT INTO users 
        (full_name_, email_, phone_, password_hash_, role_)
        VALUES (%s, %s, %s, %s, %s) 
        RETURNING id_, full_name_, email_, phone_, role_, created_at_, updated_at_"""
        return self.insert(query, (item.full_name_, item.email_, item.phone_, item.password_, item.role_))
    
    def revoke_refresh(self, token):
        query = """
        UPDATE refresh_tokens
        SET revoked_ = TRUE
        WHERE token_ = %s
        RETURNING id_, revoked_
        """
        return self.update(query, (token,))

    def revoke_all_refresh_by_email(self, email):
        query = """
        UPDATE refresh_tokens
        SET revoked_ = TRUE
        WHERE user_email_ = %s AND revoked_ = FALSE
        """
        self.execute(query, (email,))

user_interact = UserInteract()