import importlib.util
import sqlite3
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('rebuild_rehearsal', Path(__file__).resolve().parents[1] / 'scripts/rebuild_database_rehearsal.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_backup_preserves_credentials_and_relationships_without_reporting_contents(tmp_path):
    source, destination = tmp_path/'source.db', tmp_path/'backup.db'
    with sqlite3.connect(source) as db:
        db.executescript("CREATE TABLE users(id TEXT PRIMARY KEY, password_hash TEXT); CREATE TABLE plans(id TEXT, owner TEXT REFERENCES users(id)); INSERT INTO users VALUES('fixture-user','fixture-secret-hash'); INSERT INTO plans VALUES('fixture-plan','fixture-user');")
    before = source.read_bytes()
    report = module.rehearse(source, destination)
    assert report['verified'] and source.read_bytes() == before
    assert 'fixture-secret-hash' not in str(report)
    with sqlite3.connect(destination) as db:
        assert db.execute('SELECT password_hash FROM users').fetchone()[0] == 'fixture-secret-hash'
        assert db.execute('SELECT owner FROM plans').fetchone()[0] == 'fixture-user'

def test_never_overwrites_a_destination(tmp_path):
    source, destination = tmp_path/'source.db', tmp_path/'keep.db'
    with sqlite3.connect(source): pass
    destination.write_text('keep me')
    with pytest.raises(ValueError): module.rehearse(source, destination)
    assert destination.read_text() == 'keep me'
