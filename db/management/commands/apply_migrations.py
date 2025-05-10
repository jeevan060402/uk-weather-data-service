from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.migrations.loader import MigrationLoader


class Command(BaseCommand):
    help = "execute database migrations"

    # Retrieving all application names
    def extract_app_names(self):
        return [app.split(".")[-1] for app in settings.INSTALLED_APPS]

    # Fetching migrations for the specified app
    def get_app_migrations(self, app_name):
        app_migrations = []
        try:
            loader = MigrationLoader(None)
            for migration_key in loader.graph.nodes:
                if migration_key[0] == app_name:
                    app_migrations.append(migration_key[1])
        except Exception as e:
            print(f"Error retrieving migrations for {app_name}: {e}")
            return []

        return sorted(app_migrations)

    # Retrieving the last successful migration for each app
    def get_last_successfull_migration(self, app_name):
        try:
            applied_migrations = MigrationLoader(connection=connections["default"]).applied_migrations
            last_successful_migration = None
            for key, value in applied_migrations.items():
                if key[0] == app_name:
                    last_successful_migration = key[1]
            return last_successful_migration
        except Exception as e:
            print(f"Error retrieving last successful migration for {app_name}: {e}")
            return None

    # Applying migrations for all applications
    def apply_app_migrations(self, app_migration_details):
        app_name = app_migration_details["name"]
        migrations = app_migration_details["migrations"]

        for migration in migrations:
            try:
                print(f"Executing migration {migration} for {app_name}")
                call_command("migrate", app_name, migration, interactive=False)
            except Exception as e:
                print(f"Error applying migration {migration} for {app_name}: {e}")
                return

    # Reverting to the last successful migration
    def rollback_all_to_prev_successfull_migrations(self, app_migration_details):
        app_name = app_migration_details["name"]
        last_successful_migration = app_migration_details["last_successful_migration"] or "zero"
        curr_migrations_applied = self.get_last_successfull_migration(app_name) or "zero"
        if last_successful_migration == "zero" and curr_migrations_applied == "zero":
            print(f"{app_name} - No migrations applied to rollback")
            return
        print(f"{app_name} - Initiating rollback to migration {last_successful_migration}")
        try:
            call_command("migrate", app_name, last_successful_migration, interactive=False)
        except Exception as e:
            print(f"Rollback of {app_name} migration to {last_successful_migration} failed: {e}")

    # Fetching all migrations for all applications
    def get_all_migrations(self, app_names):
        all_migrations = []
        for app_name in app_names:
            try:
                migrations = self.get_app_migrations(app_name)
                last_successful_migration = self.get_last_successfull_migration(app_name)
                current_app_migrations = {
                    "name": app_name,
                    "migrations": migrations,
                    "last_successful_migration": last_successful_migration,
                }
                all_migrations.append(current_app_migrations)
            except Exception as e:
                print(f"Error processing migrations for {app_name}: {e}")
        return all_migrations

    # Executing migrations
    def migrations(self):
        app_names = self.extract_app_names()
        all_migrations = self.get_all_migrations(app_names)
        print("Migration process started")

        try:
            for app_migration in all_migrations:
                app_name = app_migration["name"]
                migrations = app_migration["migrations"]
                last_successful_migration = app_migration["last_successful_migration"]
                if not len(migrations) or last_successful_migration == migrations[-1]:
                    print(f"{app_name} - No migrations to apply")
                    continue
                self.apply_app_migrations(app_migration)
            print("Migrations completed successfully")
        except Exception as e:
            print(f"Migration process failed: {e}")
            print("Rollback Started")
            for app_migration in all_migrations:
                if app_migration["migrations"]:
                    self.rollback_all_to_prev_successfull_migrations(app_migration)

    def handle(self, *args, **kwargs):
        self.migrations()
