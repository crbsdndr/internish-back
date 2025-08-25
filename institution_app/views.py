from internish.connect import PostgresConnection


class InstitutionInteract(PostgresConnection):
    def list(self, q=None, limit=10, offset=0):
        query = """
        SELECT
            i.id_, i.name_, i.address_, i.photo_, i.notes_,
            COALESCE(
                (SELECT json_agg(ic.*) FROM institution_contacts ic WHERE ic.institution_id_ = i.id_),
                '[]'::json
            ) AS institution_contacts_,
            COALESCE(
                (SELECT json_agg(iq.*) FROM institution_quotas iq WHERE iq.institution_id_ = i.id_),
                '[]'::json
            ) AS institution_quotas_
        FROM institutions i
        WHERE (%(q)s IS NULL OR i.name_ ILIKE '%%' || %(q)s || '%%')
        ORDER BY i.id_ DESC
        LIMIT %(limit)s OFFSET %(offset)s;
        """
        return self.fetchall(query, {"q": q, "limit": limit, "offset": offset})

    def detail(self, institution_id):
        query = """
        SELECT
            i.id_, i.name_, i.address_, i.photo_, i.notes_,
            COALESCE(
                (SELECT json_agg(ic.*) FROM institution_contacts ic WHERE ic.institution_id_ = i.id_),
                '[]'::json
            ) AS institution_contacts_,
            COALESCE(
                (SELECT json_agg(iq.*) FROM institution_quotas iq WHERE iq.institution_id_ = i.id_),
                '[]'::json
            ) AS institution_quotas_
        FROM institutions i
        WHERE i.id_ = %(id)s
        LIMIT 1;
        """
        return self.fetchone(query, {"id": institution_id})

    def v_create(self, institution, institution_contacts=None, institution_quotas=None):
        with self.transaction() as cur:
            cur.execute(
                """
                INSERT INTO institutions (name_, address_, photo_, notes_)
                VALUES (%s, %s, %s, %s)
                RETURNING id_;
                """,
                (institution.name_, institution.address_, institution.photo_, institution.notes_),
            )
            result = cur.fetchone()
            institution_id = result[0]

            if institution_contacts is not None:
                cur.execute(
                    """
                    INSERT INTO institution_contacts (
                        institution_id_, name_, email_, phone_, position_, is_primary_)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (
                        institution_id,
                        institution_contacts["name_"],
                        institution_contacts.get("email_"),
                        institution_contacts.get("phone_"),
                        institution_contacts.get("position_"),
                        institution_contacts.get("is_primary_"),
                    ),
                )
            if institution_quotas is not None:
                cur.execute(
                    """
                    INSERT INTO institution_quotas (institution_id_, period_, quota_)
                    VALUES (%s, %s, %s);
                    """,
                    (
                        institution_id,
                        institution_quotas["period_"],
                        institution_quotas["quota_"],
                    ),
                )

        return True

    def v_update(
        self,
        institution_id,
        institution,
        institution_contacts=None,
        institution_quotas=None,
    ):
        with self.transaction() as cur:
            cur.execute(
                """
                UPDATE institutions
                SET name_ = %s, address_ = %s, photo_ = %s, notes_ = %s
                WHERE id_ = %s
                RETURNING id_;
                """,
                (
                    institution.name_,
                    institution.address_,
                    institution.photo_,
                    institution.notes_,
                    institution_id,
                ),
            )
            if cur.fetchone() is None:
                return False

            if institution_contacts is not None:
                cur.execute(
                    "DELETE FROM institution_contacts WHERE institution_id_ = %s",
                    (institution_id,),
                )
                cur.execute(
                    """
                    INSERT INTO institution_contacts (
                        institution_id_, name_, email_, phone_, position_, is_primary_
                    )
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (
                        institution_id,
                        institution_contacts.get("name_"),
                        institution_contacts.get("email_"),
                        institution_contacts.get("phone_"),
                        institution_contacts.get("position_"),
                        institution_contacts.get("is_primary_"),
                    ),
                )

            if institution_quotas is not None:
                cur.execute(
                    "DELETE FROM institution_quotas WHERE institution_id_ = %s",
                    (institution_id,),
                )
                cur.execute(
                    """
                    INSERT INTO institution_quotas (institution_id_, period_, quota_)
                    VALUES (%s, %s, %s);
                    """,
                    (
                        institution_id,
                        institution_quotas.get("period_"),
                        institution_quotas.get("quota_"),
                    ),
                )

        return True

    def v_delete(self, institution_id):
        with self.transaction() as cur:
            cur.execute(
                "DELETE FROM institutions WHERE id_ = %s RETURNING id_;",
                (institution_id,),
            )
            return cur.fetchone() is not None


institution_interact = InstitutionInteract()

