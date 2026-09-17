"""Explicitly isolated SQLite target for local migration rehearsals only."""
from .settings import *  # noqa: F403
import os
from pathlib import Path

target = os.environ.get('MOVENA_REHEARSAL_DATABASE')
if not target or not Path(target).is_absolute():
    raise RuntimeError('MOVENA_REHEARSAL_DATABASE must be an absolute private rehearsal path.')
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': target}}
