step("""
        create unique index unq_lib_name_association_id
            on lib (name, association_id)
     """,
     """
        drop index unq_lib_name_association_id
     """
     )

step("""
        drop index idx_lib_name
     """,
     """
        create index idx_lib_name
            on lib (name)
     """
     )
