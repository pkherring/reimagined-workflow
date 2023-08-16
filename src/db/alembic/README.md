# Generic single-database configuration.

# Configuration
When configuring the `target_metadata`, make sure to import `Base` from the models module, not the location of the parent class.

## Notes on how to use Alembic
1. Modify the model in `src/db/models.py`
2. Run `alembic revision --autogenerate -m "message"`
3. Edit the alembic migration file in `src/db/alembic/versions/` This is very important since Alembic is not perfect and may generate incorrect migrations.
4. Run `alembic upgrade head` to apply the migration to the database.

Note that Alembic does not remember the previous state of the database, so if there are earlier updates that you want to apply, you will need to run `alembic upgrade <revision>` where `<revision>` is the revision number of the migration you want to apply.
