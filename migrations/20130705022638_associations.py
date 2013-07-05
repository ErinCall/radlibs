step("""
        create table association (
            association_id serial primary key,
            name text not null
        )
    """,
    """
        drop table association
    """
)

step("""
        create table user_association (
            user_id integer references "user" (user_id),
            association_id integer references association (association_id)
        )
    """,
    """
        drop table user_association
    """
)

step("""
        create unique index unq_user_association_user_id_association_id
            on user_association (user_id, association_id)
    """,
    """
        select 1
    """
)
