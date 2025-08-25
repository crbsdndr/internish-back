from internish.connect import db, PostgresConnection

class InstitutionInteract(PostgresConnection):
    def v_create(self, institution, institution_contacts=None, institution_quotas=None):
        with self.transaction() as cur:
            cur.execute("""
                INSERT INTO institutions (name_, address_, photo_, notes_)
                VALUES (%s, %s, %s, %s)
                RETURNING id_;
            """, (institution.name_, institution.address_, institution.photo_, institution.notes_))
            result = cur.fetchone()
            institution_id = result[0]

            if institution_contacts is not None:
                cur.execute("""
                    INSERT INTO institution_contacts (
                        institution_id_, name_, email_, phone_, position_, is_primary_)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """, (
                        institution_id,
                        institution_contacts["name_"], institution_contacts["email_"],
                        institution_contacts["phone_"], institution_contacts["position_"],
                        institution_contacts["is_primary_"]
                    )
                )
            if institution_quotas is not None:
                cur.execute("""
                    INSERT INTO institution_quotas (institution_id_, period_, quota_)
                    VALUES (%s, %s, %s);
                    """, (
                        institution_id,
                        institution_quotas["period_"], institution_quotas["quota_"],
                    )
                )

        return True

institution_interact = InstitutionInteract()
