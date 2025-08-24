from internish.connect import db, PostgresConnection

class InstitutionInteract(PostgresConnection):
    def v_create(self, institution):
        with self.transaction() as cur:
            cur.execute("""
                INSERT INTO institutions (name_, address_, photo_, notes_)
                VALUES (%s, %s, %s, %s)
                RETURNING id_;
            """, (institution.name_, institution.address_, institution.photo_, institution.notes_))
            result = cur.fetchone()[0]
            return {"id": result}

            # cur.execute("""
            #     INSERT INTO students (user_id_, student_number_, national_sn_, major_, batch_, notes_, photo_)
            #     VALUES (%s, %s, %s, %s, %s, %s, %s);
            #     """, (
            #         user_id,
            #         student["student_number_"], student["national_sn_"],
            #         student["major_"], student["batch_"],
            #         student.get("notes_"), student.get("photo_")
            #     )
            # )

            # cur.execute("""
            #     INSERT INTO supervisors (user_id_, supervisor_number_, department_, notes_, photo_)
            #     VALUES (%s, %s, %s, %s, %s);
            #     """, (
            #         user_id,
            #         supervisor["supervisor_number_"], supervisor["department_"],
            #         supervisor.get("notes_"), supervisor.get("photo_")
            #     )
            # )

            # return {"id": user_id, "role": role}

institution_interact = InstitutionInteract()
