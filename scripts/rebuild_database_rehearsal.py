"""Read-only SQLite backup rehearsal with aggregate integrity evidence.

This is not a Django domain migration and never changes the source database.
Existing destinations are refused. No record contents appear in the report.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def fingerprint(connection: sqlite3.Connection) -> dict:
    tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    result = {}
    for table in tables:
        columns = list(connection.execute(f'PRAGMA table_info({quote(table)})'))
        rows = []
        for row in connection.execute(f'SELECT * FROM {quote(table)}'):
            normalized = [v.hex() if isinstance(v, bytes) else v for v in row]
            rows.append(hashlib.sha256(json.dumps(normalized, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest())
        result[table] = {'rows': len(rows), 'digest': hashlib.sha256(''.join(sorted(rows)).encode()).hexdigest(),
                         'columns': [c[1] for c in columns]}
    return {'tables': result, 'foreign_key_violations': len(list(connection.execute('PRAGMA foreign_key_check'))),
            'integrity': connection.execute('PRAGMA integrity_check').fetchone()[0]}


def rehearse(source: Path, destination: Path) -> dict:
    source, destination = source.resolve(), destination.resolve()
    if not source.is_file(): raise ValueError('Source database does not exist')
    if destination.exists() or source == destination: raise ValueError('Destination must be a new file')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as original:
        with sqlite3.connect(destination) as backup:
            original.backup(backup)
            copied = fingerprint(backup)
        # Compare with a stable source read transaction; abort the rehearsal if a
        # live writer changed records between the backup and this comparison.
        original.execute('BEGIN')
        before = fingerprint(original)
    return {'source_unchanged_by_tool': True, 'verified': before == copied and copied['integrity'] == 'ok' and copied['foreign_key_violations'] == 0,
            'tables': {name: {'rows': value['rows']} for name, value in copied['tables'].items()},
            'foreign_key_violations': copied['foreign_key_violations'], 'integrity': copied['integrity'],
            'domain_migration_performed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('source', type=Path); parser.add_argument('destination', type=Path)
    args = parser.parse_args(); report = rehearse(args.source, args.destination)
    print(json.dumps(report, indent=2)); raise SystemExit(0 if report['verified'] else 1)
