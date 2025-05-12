from django.core.management.base import BaseCommand
from django.db import connections, transaction


class Command(BaseCommand):
    help = "Create text search configuration for PostgreSQL"

    def handle(self, *args, **kwargs):
        check_query = """
            SELECT 1
            FROM pg_catalog.pg_ts_config
            WHERE cfgname = 'english_nostop'
              AND cfgnamespace = (SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = 'public')
        """

        creation_commands = [
            """
            CREATE TEXT SEARCH DICTIONARY english_stem_nostop (
                Template = snowball,
                Language = english
            );
            """,
            """
            CREATE TEXT SEARCH CONFIGURATION public.english_nostop ( COPY = pg_catalog.english );
            """,
            """
            ALTER TEXT SEARCH CONFIGURATION public.english_nostop
                ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, hword, hword_part, word WITH english_stem_nostop;
            """,
        ]

        # FOR POSTGRES
        with connections["default"].cursor() as cursor:
            cursor.execute(check_query)
            exists = cursor.fetchone()

            if not exists:
                with transaction.atomic():
                    for command in creation_commands:
                        cursor.execute(command)
                self.stdout.write(self.style.SUCCESS("Successfully created text search configuration for Postgres"))
            else:
                self.stdout.write(
                    self.style.SUCCESS("Text search configuration already exists for Postgres, skipping creation")
                )
