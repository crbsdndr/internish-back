from internish.connect import db, PostgresConnection

class UserInteract(PostgresConnection):
    def list(self):
        query = """SELECT 
                users.id_,
                users.full_name_,
                users.email_,
                users.phone_,
                users.role_,
                users.created_at_,
                students.id_ AS student_id,
                students.student_number_,
                students.national_sn_,
                students.major_,
                students.batch_,
                students.notes_ AS student_notes_,
                supervisors.id_ AS supervisor_id,
                supervisors.supervisor_number_,
                supervisors.department_,
                supervisors.notes_ AS supervisor_notes_ 
            FROM users
            LEFT JOIN students 
                ON users.id_ = students.user_id_
            LEFT JOIN supervisors 
                ON users.id_ = supervisors.user_id_;"""
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

    def create_user_with_role(self, user_item, student=None, supervisor=None):
        if self.index(email=user_item.email_):
            print("masukc")
            raise ValueError("Email already registered")

        role = user_item.role_.lower()
        if role == "student" and not student:
            raise ValueError("Student role must have student data.")

        if role == "supervisor" and not supervisor:
            raise ValueError("Supervisor role must have supervisor data.")

        if role == "developer" and (student or supervisor):
            raise ValueError("Developer role must not have student/supervisor data.")

        with self.transaction() as cur:
            cur.execute("""
                INSERT INTO users (full_name_, email_, phone_, password_hash_, role_)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_;
            """, (user_item.full_name_, user_item.email_, user_item.phone_, user_item.password_, role))
            user_id = cur.fetchone()[0]

            if role == "student":
                cur.execute("""
                    INSERT INTO students (user_id_, student_number_, national_sn_, major_, batch_, notes_, photo_)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    user_id,
                    student["student_number_"], student["national_sn_"],
                    student["major_"], student["batch_"],
                    student.get("notes_"), student.get("photo_")
                ))

            elif role == "supervisor":
                cur.execute("""
                    INSERT INTO supervisors (user_id_, supervisor_number_, department_, notes_, photo_)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    user_id,
                    supervisor["supervisor_number_"], supervisor["department_"],
                    supervisor.get("notes_"), supervisor.get("photo_")
                ))

            return {"id": user_id, "role": role}

    def revoke_refresh(self, token):
        query = """
        UPDATE refresh_tokens
        SET revoked_ = TRUE
        WHERE token_ = %s
        RETURNING id_, revoked_;
        """
        return self.update(query, (token,))

    def revoke_all_refresh_by_email(self, email):
        query = """
        UPDATE refresh_tokens
        SET revoked_ = TRUE
        WHERE user_email_ = %s AND revoked_ = FALSE;
        """
        self.execute(query, (email,))

    def save_refresh(self, email, token, expires_at):
        query = """
        INSERT INTO refresh_tokens (user_email_, token_, expires_at_)
        VALUES (%s, %s, %s)
        RETURNING id_, user_email_, token_, expires_at_, revoked_, created_at_;
        """
        return self.insert(query, (email, token, expires_at))

    def get_refresh(self, token):
        query = "SELECT * FROM refresh_tokens WHERE token_ = %s"
        return self.fetchone(query, (token,))

user_interact = UserInteract()
