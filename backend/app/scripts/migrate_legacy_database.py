"""Restore the legacy PhysioVision database contents into Movena.

The caller must stop application writes before running this command. The copy is
transactional on the destination and aborts when Movena contains an account that
does not exist in the legacy snapshot.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable

import psycopg
from alembic import command
from alembic.config import Config
from psycopg import sql


EXCLUDED_TABLES = {"alembic_version"}


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _connection(prefix: str = "") -> psycopg.Connection:
    return psycopg.connect(
        host=_required(f"{prefix}DATABASE_HOST"),
        port=int(os.environ.get(f"{prefix}DATABASE_PORT", "5432")),
        dbname=_required(f"{prefix}DATABASE_NAME"),
        user=_required(f"{prefix}DATABASE_USER"),
        password=_required(f"{prefix}DATABASE_PASSWORD"),
        connect_timeout=20,
    )


def upgrade_legacy_schema() -> None:
    """Upgrade only the isolated snapshot copy before comparing schemas."""
    database_keys = ("DATABASE_HOST", "DATABASE_PORT", "DATABASE_NAME", "DATABASE_USER", "DATABASE_PASSWORD")
    previous = {key: os.environ.get(key) for key in database_keys}
    try:
        for key in database_keys:
            legacy_key = f"LEGACY_{key}"
            if key == "DATABASE_PORT":
                os.environ[key] = os.environ.get(legacy_key, "5432")
            else:
                os.environ[key] = _required(legacy_key)
        config = Config("/app/alembic.ini")
        config.set_main_option("script_location", "/app/backend/alembic")
        command.upgrade(config, "head")
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def topological_table_order(tables: Iterable[str], dependencies: Iterable[tuple[str, str]]) -> list[str]:
    """Return parents before children for ``(child, parent)`` dependencies."""
    names = set(tables)
    parents = {name: set() for name in names}
    children = {name: set() for name in names}
    for child, parent in dependencies:
        if child in names and parent in names and child != parent:
            parents[child].add(parent)
            children[parent].add(child)
    ready = sorted(name for name, required in parents.items() if not required)
    ordered: list[str] = []
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for child in sorted(children[current]):
            parents[child].discard(current)
            if not parents[child] and child not in ordered and child not in ready:
                ready.append(child)
        ready.sort()
    if len(ordered) != len(names):
        blocked = sorted(names - set(ordered))
        raise RuntimeError(f"Foreign-key cycle prevents a guarded copy: {', '.join(blocked)}")
    return ordered


def target_only_account_emails(source: Iterable[str], target: Iterable[str]) -> set[str]:
    normalized_source = {email.strip().lower() for email in source}
    return {email.strip().lower() for email in target} - normalized_source


def _tables(connection: psycopg.Connection) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT table_name FROM information_schema.tables
               WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"""
        )
        return {row[0] for row in cursor.fetchall()} - EXCLUDED_TABLES


def _dependencies(connection: psycopg.Connection) -> list[tuple[str, str]]:
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT child.relname, parent.relname
               FROM pg_constraint constraint_row
               JOIN pg_class child ON child.oid = constraint_row.conrelid
               JOIN pg_class parent ON parent.oid = constraint_row.confrelid
               JOIN pg_namespace namespace_row ON namespace_row.oid = child.relnamespace
               WHERE constraint_row.contype = 'f' AND namespace_row.nspname = 'public'"""
        )
        return [(row[0], row[1]) for row in cursor.fetchall()]


def _columns(connection: psycopg.Connection, table: str) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT column_name FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = %s
               ORDER BY ordinal_position""",
            (table,),
        )
        return [row[0] for row in cursor.fetchall()]


def _account_emails(connection: psycopg.Connection) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT email FROM users")
        return [row[0] for row in cursor.fetchall()]


def _schema_version(connection: psycopg.Connection) -> str:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version_num FROM alembic_version")
        value = cursor.fetchone()
        if not value:
            raise RuntimeError("Database has no Alembic schema version")
        return value[0]


def _credential_digest(connection: psycopg.Connection) -> str:
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT user_id, username, email, password_hash, role, is_active,
                      is_verified, account_status, is_protected, token_version
               FROM users ORDER BY user_id"""
        )
        payload = json.dumps(cursor.fetchall(), default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _copy_table(source: psycopg.Connection, target: psycopg.Connection, table: str) -> int:
    source_columns = _columns(source, table)
    target_columns = set(_columns(target, table))
    columns = [column for column in source_columns if column in target_columns]
    if not columns:
        raise RuntimeError(f"No common columns for {table}")
    select_query = sql.SQL("SELECT {} FROM {}").format(
        sql.SQL(", ").join(map(sql.Identifier, columns)), sql.Identifier(table)
    )
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, columns)),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns),
    )
    copied = 0
    with source.cursor() as source_cursor, target.cursor() as target_cursor:
        source_cursor.execute(select_query)
        while rows := source_cursor.fetchmany(500):
            target_cursor.executemany(insert_query, rows)
            copied += len(rows)
    return copied


def _reset_sequences(connection: psycopg.Connection, tables: Iterable[str]) -> None:
    with connection.cursor() as cursor:
        for table in tables:
            cursor.execute(
                """SELECT column_name FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = %s
                     AND column_default LIKE 'nextval(%%'""",
                (table,),
            )
            for (column,) in cursor.fetchall():
                cursor.execute("SELECT pg_get_serial_sequence(%s, %s)", (f"public.{table}", column))
                sequence = cursor.fetchone()[0]
                if sequence:
                    cursor.execute(
                        sql.SQL("SELECT setval(%s, COALESCE(MAX({}), 1), MAX({}) IS NOT NULL) FROM {}").format(
                            sql.Identifier(column), sql.Identifier(column), sql.Identifier(table)
                        ),
                        (sequence,),
                    )


def migrate() -> dict[str, object]:
    upgrade_legacy_schema()
    with _connection("LEGACY_") as source, _connection() as target:
        source_version = _schema_version(source)
        target_version = _schema_version(target)
        if source_version != target_version:
            raise RuntimeError(f"Schema mismatch: legacy={source_version}, movena={target_version}")

        source_tables = _tables(source)
        target_tables = _tables(target)
        if source_tables != target_tables:
            raise RuntimeError(
                "Table mismatch: "
                f"legacy_only={sorted(source_tables - target_tables)}, "
                f"movena_only={sorted(target_tables - source_tables)}"
            )

        target_only = target_only_account_emails(_account_emails(source), _account_emails(target))
        if target_only:
            raise RuntimeError(
                f"Movena has {len(target_only)} account(s) absent from the snapshot; refusing replacement"
            )

        ordered_tables = topological_table_order(source_tables, _dependencies(target))
        source_user_count = len(_account_emails(source))
        target_user_count_before = len(_account_emails(target))
        source_digest = _credential_digest(source)

        with target.transaction():
            truncate = sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE").format(
                sql.SQL(", ").join(map(sql.Identifier, ordered_tables))
            )
            target.execute(truncate)
            copied = {table: _copy_table(source, target, table) for table in ordered_tables}
            _reset_sequences(target, ordered_tables)
            if _credential_digest(target) != source_digest:
                raise RuntimeError("Account credential verification failed; destination transaction rolled back")
            with target.cursor() as cursor:
                for table, expected in copied.items():
                    cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
                    actual = cursor.fetchone()[0]
                    if actual != expected:
                        raise RuntimeError(f"Row-count verification failed for {table}: {actual} != {expected}")

        return {
            "status": "migrated",
            "schema_version": source_version,
            "legacy_users": source_user_count,
            "movena_users_before": target_user_count_before,
            "movena_users_after": source_user_count,
            "tables_copied": len(ordered_tables),
            "rows_copied": sum(copied.values()),
        }


if __name__ == "__main__":
    print(json.dumps(migrate(), sort_keys=True))
