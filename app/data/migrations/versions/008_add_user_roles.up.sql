ALTER TABLE DEFAULT_SCHEMA.users
    ADD COLUMN roles varchar(30) NOT NULL DEFAULT 'USER'
        CONSTRAINT chk_users_roles
            CHECK (roles IN ('USER', 'ADMIN'));