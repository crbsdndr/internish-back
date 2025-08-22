from internish.connect import db, PostgresConnection

class UserInteract(PostgresConnection):
    # Boleh juga tidak inherit, tapi pakai 'db' yang diimport. Di sini saya inherit biar akses .transaction()

    def list(self):
        q = "SELECT * FROM users ORDER BY id_ DESC"
        return self.fetchall(q)

    def index(self, id=None, email=None):
        if (id is not None) and (email is not None):
            raise ValueError("Provide only one parameter: either 'id' or 'email', not both.")
        if (id is None) and (email is None):
            raise ValueError("You must provide either 'id' or 'email'.")

        if id is not None:
            q = "SELECT * FROM users WHERE id_ = %s"
            return self.fetchone(q, (id,))
        else:
            q = "SELECT * FROM users WHERE email_ = %s"
            return self.fetchone(q, (email,))

    def create_user_with_role(self, user_item, student=None, supervisor=None):
        """
        user_item: object/namespace punya .full_name_, .email_, .phone_, .password_, .role_
        student/supervisor: dict/obj detail sesuai role (atau None)
        - Insert users
        - Jika role student/supervisor → insert ke tabel pendamping
        - Semua dalam 1 transaksi (commit di akhir).
        """
        role = user_item.role_.lower()
        if role == "student" and not student:
            raise ValueError("Role student membutuhkan data students.")
        if role == "supervisor" and not supervisor:
            raise ValueError("Role supervisor membutuhkan data supervisors.")
        if role == "developer" and (student or supervisor):
            raise ValueError("Developer tidak boleh punya data student/supervisor.")

        with self.transaction() as cur:
            # 1) insert users
            cur.execute("""
                INSERT INTO users (full_name_, email_, phone_, password_hash_, role_)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_;
            """, (user_item.full_name_, user_item.email_, user_item.phone_, user_item.password_, role))
            user_id = cur.fetchone()[0]

            # 2) tabel pendamping
            if role == "student":
                cur.execute("""
                    INSERT INTO students (user_id_, student_number_, national_sn_, major_, batch_, notes_, photo_)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    user_id,
                    student["student_number"], student["national_sn"],
                    student["major"], student["batch"],
                    student.get("notes"), student.get("photo")
                ))

            elif role == "supervisor":
                cur.execute("""
                    INSERT INTO supervisors (user_id_, supervisor_number_, department_, notes_, photo_)
                    VALUES (%s, %s, %s, %s, %s);
                """, (
                    user_id,
                    supervisor["supervisor_number"], supervisor["department"],
                    supervisor.get("notes"), supervisor.get("photo")
                ))

            # 3) commit otomatis saat keluar from self.transaction()
            return {"id": user_id, "role": role}

    # --- refresh token utilities (perbaiki: kamu pakai update() tapi di connect.py semula belum ada) ---
    def revoke_refresh(self, token):
        q = """
        UPDATE refresh_tokens
        SET revoked_ = TRUE
        WHERE token_ = %s
        RETURNING id_, revoked_;
        """
        return self.update(q, (token,))

    def revoke_all_refresh_by_email(self, email):
        q = """
        UPDATE refresh_tokens
        SET revoked_ = TRUE
        WHERE user_email_ = %s AND revoked_ = FALSE;
        """
        self.execute(q, (email,))

    def save_refresh(self, email, token, expires_at):
        q = """
        INSERT INTO refresh_tokens (user_email_, token_, expires_at_)
        VALUES (%s, %s, %s)
        RETURNING id_, user_email_, token_, expires_at_, revoked_, created_at_;
        """
        return self.insert(q, (email, token, expires_at))

    def get_refresh(self, token):
        q = "SELECT * FROM refresh_tokens WHERE token_ = %s"
        return self.fetchone(q, (token,))

user_interact = UserInteract()
