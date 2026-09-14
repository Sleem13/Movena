"""Rehearse snapshot-bound identity ownership transfer and database rollback."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def run(source,target,rollback):
    source,target,rollback=map(lambda p:Path(p).resolve(),(source,target,rollback))
    if not source.is_file() or target.exists() or rollback.exists() or len({source,target,rollback}) != 3:
        raise ValueError('Source must exist and both rehearsal targets must be distinct and new.')
    source_before=hashlib.sha256(source.read_bytes()).hexdigest()
    target.parent.mkdir(parents=True,exist_ok=True)
    target.touch(exist_ok=False)
    confirmation='rehearsal-transfer-confirmation-'+'x'*40
    env={**os.environ,'DJANGO_SETTINGS_MODULE':'movena.rehearsal_settings',
         'MOVENA_REHEARSAL_DATABASE':str(target),'MOVENA_IDENTITY_MODE':'legacy',
         'MOVENA_IDENTITY_TRANSFER_CONFIRMATION':confirmation}
    def manage(*args):
        result=subprocess.run([sys.executable,str(ROOT/'services/platform/manage.py'),*args],
            cwd=ROOT,env=env,text=True,capture_output=True,timeout=120)
        if result.returncode:
            raise RuntimeError('Isolated ownership rehearsal command failed.')
        return result.stdout
    manage('migrate','--noinput','--verbosity','0')
    manage('import_identity_snapshot',str(source),'--persist')
    shutil.copy2(target,rollback)
    report=json.loads(manage('transfer_identity_ownership',str(source),'--execute'))
    with sqlite3.connect(source) as old, sqlite3.connect(target) as new:
        old_versions=dict(old.execute('SELECT user_id,token_version FROM users'))
        new_rows=list(new.execute('SELECT user_id,token_version,credential_owner FROM identity_account'))
        owners_platform=all(owner=='platform' for _,_,owner in new_rows)
        versions_advanced=all(version==old_versions[user_id]+1 for user_id,version,_ in new_rows)
        conversion_intents=new.execute("SELECT COUNT(*) FROM identity_identityoutbox WHERE event_type='account.ownership_transfer_requested' AND published_at IS NULL").fetchone()[0]
    env['MOVENA_REHEARSAL_DATABASE']=str(rollback)
    rollback_verified=json.loads(manage('import_identity_snapshot',str(source)))['verified']
    with sqlite3.connect(rollback) as restored:
        rollback_legacy=restored.execute("SELECT COUNT(*) FROM identity_account WHERE credential_owner='legacy'").fetchone()[0]
    source_unchanged=source_before==hashlib.sha256(source.read_bytes()).hexdigest()
    verified=(report['verified'] and owners_platform and versions_advanced
              and conversion_intents==report['accounts'] and rollback_verified
              and rollback_legacy==report['accounts'] and source_unchanged)
    return {**report,'verified':verified,'all_token_versions_advanced_once':versions_advanced,
        'all_accounts_platform_owned':owners_platform,'pending_legacy_conversion_intents':conversion_intents,
        'rollback_restored_legacy_ownership':rollback_legacy==report['accounts'],
        'source_bytes_unchanged':source_unchanged,'production_cutover_performed':False,
        'legacy_conversion_endpoint_called':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('source',type=Path)
    parser.add_argument('target',type=Path); parser.add_argument('rollback',type=Path)
    parser.add_argument('--output',type=Path); args=parser.parse_args()
    try: result=run(args.source,args.target,args.rollback)
    except (ValueError,RuntimeError):
        raise SystemExit('Identity ownership rehearsal failed in isolated files.') from None
    rendered=json.dumps(result,indent=2)+'\n'
    if args.output: args.output.write_text(rendered,encoding='utf-8')
    print(rendered); raise SystemExit(0 if result['verified'] else 1)
