step("""
        create table lib (
            lib_id serial primary key,
            name text not null,
            association_id integer
                references association (association_id)
                not null
        )
    """,
    """
        drop table lib
    """
)

step("""
        create table rad (
            rad_id serial primary key,
            rad text not null,
            lib_id integer
                references lib (lib_id)
                not null,
            created_by integer
                references "user" (user_id)
                not null,
            created_at timestamp with time zone not null
        )
    """,
    """
        drop table rad
    """
)
