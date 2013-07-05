step("""
        create table "user" (
            user_id serial primary key,
            email text,
            identifier text
    )
    """ ,
    """
        drop table "user"
    """)

step("""
        create unique index unq_user_email
            on "user" (email)
    """,
    """
        select 1
    """)

step("""
        create unique index unq_user_identifier
            on "user" (identifier)
    """,
    """
        select 1
    """)
