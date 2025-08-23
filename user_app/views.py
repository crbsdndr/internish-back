from internish.connect import db, PostgresConnection

class UserInteract(PostgresConnection):
    def list(self, q=None, limit=10, offset=0):
        query = """
        SELECT
        json_build_object(
            'id_',         users.id_,
            'full_name_',  users.full_name_,
            'email_',      users.email_,
            'phone_',      users.phone_,
            'role_',       users.role_,
            'created_at_', users.created_at_,
            'student_',    CASE WHEN students.id_    IS NOT NULL THEN row_to_json(students)    ELSE NULL END,
            'supervisor_', CASE WHEN supervisors.id_ IS NOT NULL THEN row_to_json(supervisors) ELSE NULL END
        ) AS data,
        COUNT(*) OVER() AS total
        FROM users
        LEFT JOIN students    ON students.user_id_    = users.id_
        LEFT JOIN supervisors ON supervisors.user_id_ = users.id_
        WHERE (
        %(q)s IS NULL
        OR users.full_name_ ILIKE '%%' || %(q)s || '%%'
        OR users.email_     ILIKE '%%' || %(q)s || '%%'
        )
        ORDER BY users.id_ DESC
        LIMIT %(limit)s OFFSET %(offset)s;

        """
        rows = self.fetchall(query, {"q": q, "limit": limit, "offset": offset})

        items = [row["data"] for row in rows]
        total = rows[0]["total"] if rows else 0

        from_idx = (offset + 1) if total > 0 else 0
        to_idx   = min(offset + limit, total)

        has_next = (offset + limit) < total
        has_prev = offset > 0

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "from": from_idx,
            "to": to_idx,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_offset": (offset + limit) if has_next else None,
            "prev_offset": max(offset - limit, 0) if has_prev else None,
        }

    def detail(self, id: int = None, email: str | None = None):
        if (id is None) and (email is None):
            raise ValueError("Provide id or email")
        if (id is not None) and (email is not None):
            raise ValueError("Only one of id or email")

        where = "users.id_ = %(id)s" if id is not None else "LOWER(users.email_) = LOWER(%(email)s)"
        params = {"id": id, "email": email}

        query = f"""
        SELECT json_build_object(
            'id_',         users.id_,
            'full_name_',  users.full_name_,
            'email_',      users.email_,
            'phone_',      users.phone_,
            'role_',       users.role_,
            'created_at_', users.created_at_,
            'student_',    CASE WHEN students.id_ IS NOT NULL THEN json_build_object(
                'id_', students.id_,
                'student_number_', students.student_number_,
                'national_sn_',    students.national_sn_,
                'major_',          students.major_,
                'batch_',          students.batch_,
                'notes_',          students.notes_,
                'photo_',          students.photo_
            ) ELSE NULL END,
            'supervisor_', CASE WHEN supervisors.id_ IS NOT NULL THEN json_build_object(
                'id_', supervisors.id_,
                'supervisor_number_', supervisors.supervisor_number_,
                'department_',        supervisors.department_,
                'notes_',             supervisors.notes_,
                'photo_',             supervisors.photo_
            ) ELSE NULL END
        ) AS data
        FROM users
        LEFT JOIN students    ON students.user_id_    = users.id_
        LEFT JOIN supervisors ON supervisors.user_id_ = users.id_
        WHERE {where}
        LIMIT 1;
        """

        rows = self.fetchall(query, params)
        return rows[0]["data"] if rows else None


    def create_user_with_role(self, user_item, student=None, supervisor=None):
        if self.detail(email=user_item.email_):
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

    def nfijoiskn(self, email: str):
        query = """
            SELECT id_, email_, password_hash_, role_
            FROM users
            WHERE LOWER(email_) = LOWER(%(email)s)
            LIMIT 1;
        """
        return self.fetchone(query, {"email": email})
user_interact = UserInteract()
