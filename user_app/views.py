from internish.connect import PostgresConnection

class UserInteract(PostgresConnection):
    def list(self):
        query = "SELECT * FROM users"
        return self.fetchall(query)

    def index(self, id=None, email=None):
        if (id is not None) and (email is not None):
            raise ValueError("Provide only one parameter: either 'id' or 'email', not both.")

        if (id is None) and (email is None):
            raise ValueError("You must provide either 'id' or 'email'.")

        if id is not None:
            query = "SELECT * FROM users WHERE id_ = %s"
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
    
    def save_refresh(self, email, token, expires_at):
        query = """
        INSERT INTO refresh_tokens (user_email_, token_, expires_at_)
        VALUES (%s, %s, %s)
        RETURNING id_, user_email_, token_, expires_at_, revoked_, created_at_
        """
        return self.insert(query, (email, token, expires_at))

    def get_refresh(self, token):
        query = "SELECT * FROM refresh_tokens WHERE token_ = %s"
        return self.fetchone(query, (token,))

user_interact = UserInteract()