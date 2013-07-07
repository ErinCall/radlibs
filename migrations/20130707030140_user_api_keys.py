step("""
        alter table "user"
            add column api_key text
     """,
     """
        alter table "user"
            drop column api_key
     """
     )
