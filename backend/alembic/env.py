from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import database_url_from_environment
from app.db.database import Base
from app.db import models  # noqa: F401

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
# Alembic stores options in ConfigParser, where percent characters are
# interpolation markers. Managed database passwords can legitimately contain
# them, so escape the completed URL before assigning it to the config.
config.set_main_option(
    "sqlalchemy.url",
    database_url_from_environment(config.get_main_option("sqlalchemy.url")).replace("%", "%%"),
)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"}, compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
