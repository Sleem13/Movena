"""Import a backup into a NEW private Django SQLite target and verify restore.

Usage: python scripts/rebuild_identity_rehearsal.py SOURCE NEW_TARGET NEW_RESTORE
Only aggregate evidence is printed. Run with the replacement Python environment.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from contextlib import closing
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(source, target, restore):
    paths = [Path(path).resolve() for path in (source, target, restore)]
    source, target, restore = paths
    if len(set(paths)) != 3 or not source.is_file() or target.exists() or restore.exists():
        raise ValueError('Source must exist and both destinations must be distinct new files.')
    with source.open('rb') as stream:
        before = hashlib.file_digest(stream, 'sha256').hexdigest()
    target.parent.mkdir(parents=True, exist_ok=True)
    restore.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidentally migrating an existing database.
    with target.open('xb'):
        pass
    with restore.open('xb'):
        pass
    env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'movena.rehearsal_settings',
           'MOVENA_REHEARSAL_DATABASE': str(target)}
    def manage(*arguments):
        command = [sys.executable, str(ROOT/'services/platform/manage.py'), *arguments]
        result = subprocess.run(command, env=env, cwd=ROOT, capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise RuntimeError('Isolated identity rehearsal failed. No live service was changed.')
        return result.stdout
    manage('migrate', '--noinput', '--verbosity', '0')
    imported = json.loads(manage('import_identity_snapshot', str(source), '--persist'))
    repeated = json.loads(manage('import_identity_snapshot', str(source), '--persist'))
    with closing(sqlite3.connect(target.as_uri()+'?mode=ro', uri=True)) as original:
        with closing(sqlite3.connect(restore)) as restored:
            original.backup(restored)
    env['MOVENA_REHEARSAL_DATABASE'] = str(restore)
    verified_restore = json.loads(manage('import_identity_snapshot', str(source)))
    with closing(sqlite3.connect(restore.as_uri()+'?mode=ro', uri=True)) as restored:
        integrity = restored.execute('PRAGMA integrity_check').fetchone()[0]
        violations = len(restored.execute('PRAGMA foreign_key_check').fetchall())
    with source.open('rb') as stream:
        unchanged = before == hashlib.file_digest(stream, 'sha256').hexdigest()
    verified = unchanged and repeated['inserted'] == 0 and verified_restore['inserted'] == 0 and integrity == 'ok' and violations == 0
    return {**imported, 'verified': verified, 'repeat_import_unchanged': repeated['inserted'] == 0,
            'restore_verified': verified_restore['verified'], 'source_bytes_unchanged': unchanged,
            'integrity': integrity, 'foreign_key_violations': violations,
            'production_cutover_performed': False, 'real_account_passwords_tested': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('target', type=Path)
    parser.add_argument('restore', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.resolve() in {args.source.resolve(), args.target.resolve(), args.restore.resolve()}:
        raise SystemExit('Evidence output must not overwrite a source or rehearsal database.')
    try:
        report = run(args.source, args.target, args.restore)
    except (ValueError, RuntimeError):
        raise SystemExit('Identity rehearsal failed; inspect the isolated configuration and reviewed schema mapping.') from None
    result = json.dumps(report, indent=2)+'\n'
    if args.output:
        args.output.write_text(result, encoding='utf-8')
    print(result)
    raise SystemExit(0 if report['verified'] else 1)
