step("""
        create table association_invite (
            association_id integer
                references association (association_id),
            email text,
            token text not null,
            constraint association_invite_pk
                primary key (association_id, email)
        )
     """,
     """
        drop table association_invite
     """
     )
