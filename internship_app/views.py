from internish.connect import PostgresConnection


class InternshipInteract(PostgresConnection):
    def get_student_id_by_email(self, email: str):
        query = """
        SELECT students.id_
        FROM users
        JOIN students ON students.user_id_ = users.id_
        WHERE LOWER(users.email_) = LOWER(%(email)s)
        LIMIT 1;
        """
        row = self.fetchone(query, {"email": email})
        return row["id_"] if row else None

    def _check_application(self, application_id, student_id=None):
        query = """
        SELECT student_id_, status_, deleted_at_
        FROM applications
        WHERE id_ = %(id)s
        LIMIT 1;
        """
        row = self.fetchone(query, {"id": application_id})
        if row is None:
            raise Exception("Application not found")
        if row["status_"] != "accepted" or row["deleted_at_"] is not None:
            raise Exception("Application must be accepted and active")
        if student_id is not None and row["student_id_"] != student_id:
            raise Exception("Forbidden")
        return True

    def list(self, student_id=None, limit=10, offset=0):
        query = """
        SELECT
        json_build_object(
            'id_',         i.id_,
            'application_id_', i.application_id_,
            'supervisor_id_', i.supervisor_id_,
            'start_date_', i.start_date_,
            'end_date_',   i.end_date_,
            'status_',     i.status_
        ) AS data,
        COUNT(*) OVER() AS total
        FROM internships i
        JOIN applications a ON a.id_ = i.application_id_
        WHERE a.deleted_at_ IS NULL
          AND (%(student_id)s IS NULL OR a.student_id_ = %(student_id)s)
        ORDER BY i.id_ DESC
        LIMIT %(limit)s OFFSET %(offset)s;
        """
        rows = self.fetchall(query, {"student_id": student_id, "limit": limit, "offset": offset})
        items = [row["data"] for row in rows]
        total = rows[0]["total"] if rows else 0
        from_idx = (offset + 1) if total > 0 else 0
        to_idx = min(offset + limit, total)
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

    def detail(self, internship_id, student_id=None):
        query = """
        SELECT json_build_object(
            'id_',         i.id_,
            'application_id_', i.application_id_,
            'supervisor_id_', i.supervisor_id_,
            'start_date_', i.start_date_,
            'end_date_',   i.end_date_,
            'status_',     i.status_
        ) AS data
        FROM internships i
        JOIN applications a ON a.id_ = i.application_id_
        WHERE i.id_ = %(id)s
          AND a.deleted_at_ IS NULL
          AND (%(student_id)s IS NULL OR a.student_id_ = %(student_id)s)
        LIMIT 1;
        """
        rows = self.fetchall(query, {"id": internship_id, "student_id": student_id})
        return rows[0]["data"] if rows else None

    def v_create(self, internship, student_id=None):
        self._check_application(internship.application_id_, student_id)
        query = """
        INSERT INTO internships (application_id_, supervisor_id_, start_date_, end_date_, status_)
        VALUES (%(application_id)s, %(supervisor_id)s, %(start_date)s, %(end_date)s, %(status)s)
        RETURNING id_;
        """
        result = self.insert(
            query,
            {
                "application_id": internship.application_id_,
                "supervisor_id": internship.supervisor_id_,
                "start_date": internship.start_date_,
                "end_date": internship.end_date_,
                "status": internship.status_,
            },
        )
        return result is not None

    def v_update(self, internship_id, internship, student_id=None):
        existing = self.fetchone(
            """
            SELECT i.application_id_
            FROM internships i
            WHERE i.id_ = %(id)s
            """,
            {"id": internship_id},
        )
        if existing is None:
            return False
        self._check_application(existing["application_id_"] , student_id)
        query = """
        UPDATE internships
        SET
            supervisor_id_ = %(supervisor_id)s,
            start_date_ = %(start_date)s,
            end_date_ = %(end_date)s,
            status_ = COALESCE(%(status)s, status_)
        WHERE id_ = %(id)s
        RETURNING id_;
        """
        result = self.update(
            query,
            {
                "id": internship_id,
                "supervisor_id": internship.supervisor_id_,
                "start_date": internship.start_date_,
                "end_date": internship.end_date_,
                "status": internship.status_,
            },
        )
        return result is not None

    def v_delete(self, internship_id, student_id=None):
        existing = self.fetchone(
            """
            SELECT i.application_id_
            FROM internships i
            WHERE i.id_ = %(id)s
            """,
            {"id": internship_id},
        )
        if existing is None:
            return False
        self._check_application(existing["application_id_"] , student_id)
        query = """
        DELETE FROM internships
        WHERE id_ = %(id)s
        RETURNING id_;
        """
        result = self.update(query, {"id": internship_id})
        return result is not None


internship_interact = InternshipInteract()
