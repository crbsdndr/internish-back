from internish.connect import PostgresConnection


class ApplicationInteract(PostgresConnection):
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

    def list(self, student_id=None, limit=10, offset=0):
        query = """
        SELECT
        json_build_object(
            'id_',         a.id_,
            'student_id_', a.student_id_,
            'institution_id_', a.institution_id_,
            'period_',     a.period_,
            'status_',     a.status_,
            'notes_',      a.notes_,
            'applied_at_', a.applied_at_
        ) AS data,
        COUNT(*) OVER() AS total
        FROM applications a
        WHERE a.deleted_at_ IS NULL
          AND (%(student_id)s IS NULL OR a.student_id_ = %(student_id)s)
        ORDER BY a.id_ DESC
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

    def detail(self, application_id, student_id=None):
        query = """
        SELECT json_build_object(
            'id_',         a.id_,
            'student_id_', a.student_id_,
            'institution_id_', a.institution_id_,
            'period_',     a.period_,
            'status_',     a.status_,
            'notes_',      a.notes_,
            'applied_at_', a.applied_at_
        ) AS data
        FROM applications a
        WHERE a.id_ = %(id)s AND a.deleted_at_ IS NULL
          AND (%(student_id)s IS NULL OR a.student_id_ = %(student_id)s)
        LIMIT 1;
        """
        rows = self.fetchall(query, {"id": application_id, "student_id": student_id})
        return rows[0]["data"] if rows else None

    def v_create(self, application):
        query = """
        INSERT INTO applications (student_id_, institution_id_, period_, status_, notes_)
        VALUES (%(student_id)s, %(institution_id)s, %(period)s, %(status)s, %(notes)s)
        RETURNING id_;
        """
        result = self.insert(
            query,
            {
                "student_id": application.student_id_,
                "institution_id": application.institution_id_,
                "period": application.period_,
                "status": application.status_,
                "notes": application.notes_,
            },
        )
        return result is not None

    def v_update(self, application_id, application, student_id=None):
        query = """
        UPDATE applications
        SET
            institution_id_ = %(institution_id)s,
            period_ = %(period)s,
            status_ = COALESCE(%(status)s, status_),
            notes_ = %(notes)s
        WHERE id_ = %(id)s
          AND deleted_at_ IS NULL
          AND (%(student_id)s IS NULL OR student_id_ = %(student_id)s)
        RETURNING id_;
        """
        result = self.update(
            query,
            {
                "id": application_id,
                "institution_id": application.institution_id_,
                "period": application.period_,
                "status": application.status_,
                "notes": application.notes_,
                "student_id": student_id,
            },
        )
        return result is not None

    def v_delete(self, application_id, student_id=None):
        query = """
        UPDATE applications
        SET deleted_at_ = NOW()
        WHERE id_ = %(id)s
          AND deleted_at_ IS NULL
          AND (%(student_id)s IS NULL OR student_id_ = %(student_id)s)
        RETURNING id_;
        """
        result = self.update(query, {"id": application_id, "student_id": student_id})
        return result is not None


application_interact = ApplicationInteract()
