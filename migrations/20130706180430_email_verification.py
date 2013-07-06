step("""
        alter table "user"
            add column email_verified_at
                timestamp with time zone
     """,
     """
        alter table "user"
            drop column email_verified_at
     """
     )

step("""
        create index idx_user_email_verified_at
            on "user" (email_verified_at)
     """,
     """
        drop index idx_user_email_verified_at
     """
     )

step("""
        create table email_verification_token(
            user_id integer references "user" (user_id),
            token text,
            constraint pk_email_verification_token
                primary key (user_id, token)
        )
     """,
     """
        drop table email_verification_token
     """
     )
