CREATE DATABASE internish;

\c internish;

CREATE TABLE users (
    id_ SERIAL PRIMARY KEY,
    full_name_ VARCHAR(100) NOT NULL,
    email_ VARCHAR(100) UNIQUE NOT NULL,
    phone_ VARCHAR(20) UNIQUE NOT NULL,
    password_hash_ TEXT NOT NULL,
    role_ VARCHAR(20) NOT NULL CHECK (role_ IN ('student', 'supervisor', 'developer')),
    created_at_ TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE students (
    id_ SERIAL PRIMARY KEY,
    user_id_ INT UNIQUE REFERENCES users(id_) ON DELETE CASCADE,
    student_number_ VARCHAR(50) UNIQUE NOT NULL,
    national_sn_ VARCHAR(50) NOT NULL,
    major_ VARCHAR(100) NOT NULL,
    batch_ VARCHAR(9) NOT NULL,
    notes_ TEXT,
    photo_ TEXT
);

CREATE TABLE supervisors (
    id_ SERIAL PRIMARY KEY,
    user_id_ INT UNIQUE REFERENCES users(id_) ON DELETE CASCADE,
    supervisor_number_ VARCHAR(50) UNIQUE NOT NULL,
    department_ VARCHAR(100) NOT NULL,
    notes_ TEXT
    photo_ TEXT,
);

CREATE TABLE institutions (
    id_ SERIAL PRIMARY KEY,
    name_ VARCHAR(150) NOT NULL,
    address_ TEXT NOT NULL,
    photo_ TEXT,
    notes_ TEXT
);

CREATE TABLE institution_contacts (
    id_ SERIAL PRIMARY KEY,
    institution_id_ INT NOT NULL REFERENCES institutions(id_) ON DELETE CASCADE,
    name_ VARCHAR(100) NOT NULL,
    email_ VARCHAR(100),
    phone_ VARCHAR(20),
    position_ VARCHAR(100),
    is_primary_ BOOLEAN DEFAULT FALSE
);

CREATE TABLE institution_quotas (
    id_ SERIAL PRIMARY KEY,
    institution_id_ INT NOT NULL REFERENCES institutions(id_) ON DELETE CASCADE,
    period_ VARCHAR(20) NOT NULL,
    quota_ INT NOT NULL
);

CREATE TABLE applications (
    id_ SERIAL PRIMARY KEY,
    student_id_ INT NOT NULL REFERENCES students(id_) ON DELETE CASCADE,
    institution_id_ INT NOT NULL REFERENCES institutions(id_) ON DELETE CASCADE,
    period_ VARCHAR(20),
    status_ VARCHAR(20) DEFAULT 'pending',
    notes_ TEXT,
    applied_at_ TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE internships (
    id_ SERIAL PRIMARY KEY,
    application_id_ INT NOT NULL REFERENCES applications(id_) ON DELETE CASCADE,
    supervisor_id_ INT REFERENCES supervisors(id_) ON DELETE SET NULL,
    start_date_ DATE,
    end_date_ DATE,
    status_ VARCHAR(20) DEFAULT 'ongoing'
);

CREATE TABLE monitoring_logs (
    id_ SERIAL PRIMARY KEY,
    internship_id_ INT NOT NULL REFERENCES internships(id_) ON DELETE CASCADE,
    supervisor_id_ INT NOT NULL REFERENCES supervisors(id_) ON DELETE CASCADE,
    visit_date_ DATE NOT NULL,
    skor_ INT NOT NULL,
    notes_ TEXT,
    created_at_ TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
    id_ SERIAL PRIMARY KEY,
    user_email_ VARCHAR(100) NOT NULL,
    token_ TEXT NOT NULL UNIQUE,
    expires_at_ TIMESTAMPTZ NOT NULL,
    revoked_ BOOLEAN DEFAULT FALSE,
    created_at_ TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE internships
  ADD CONSTRAINT uq_internships_application UNIQUE (application_id_);

ALTER TABLE applications
  ADD CONSTRAINT chk_applications_status CHECK (status_ IN ('pending', 'testing', 'accepted', 'rejected', 'under_review'));

ALTER TABLE internships
  ADD CONSTRAINT chk_internships_status CHECK (status_ IN ('ongoing', 'completed', 'cancelled'));

ALTER TABLE internships
  ADD CONSTRAINT chk_internships_dates CHECK (end_date_ IS NULL OR start_date_ IS NULL OR end_date_ >= start_date_);

ALTER TABLE applications
  ADD CONSTRAINT uq_applications_unique_per_period UNIQUE (student_id_, institution_id_, period_);

ALTER TABLE institution_quotas
  ADD CONSTRAINT uq_institution_quotas_period UNIQUE (institution_id_, period_);

CREATE UNIQUE INDEX ux_institution_contacts_primary
  ON institution_contacts (institution_id_)
  WHERE is_primary_ = TRUE;

ALTER TABLE students
  ADD CONSTRAINT uq_students_national_sn UNIQUE (national_sn_);

CREATE INDEX idx_applications_student ON applications(student_id_);
CREATE INDEX idx_applications_institution_period ON applications(institution_id_, period_);
CREATE INDEX idx_internships_supervisor ON internships(supervisor_id_);
CREATE INDEX idx_monitoring_logs_internship_supervisor_visit ON monitoring_logs(internship_id_, supervisor_id_, visit_date_);

CREATE OR REPLACE FUNCTION check_user_role() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.role_ = 'student' THEN
        IF NOT EXISTS (
            SELECT 1 FROM students s WHERE s.user_id_ = NEW.id_
        ) THEN
            RAISE EXCEPTION 'User(role=student) must have a row in students (user_id=%)', NEW.id_;
        END IF;

    ELSIF NEW.role_ = 'supervisor' THEN
        IF NOT EXISTS (
            SELECT 1 FROM supervisors su WHERE su.user_id_ = NEW.id_
        ) THEN
            RAISE EXCEPTION 'User(role=supervisor) must have a row in supervisors (user_id=%)', NEW.id_;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_user_role ON users;

CREATE CONSTRAINT TRIGGER trg_check_user_role
AFTER INSERT OR UPDATE ON users
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION check_user_role();
