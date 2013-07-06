step("""
        create index idx_lib_name
            on lib (name)
     """,
     """
        drop index idx_lib_name
     """
     )
