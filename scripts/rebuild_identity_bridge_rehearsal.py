"""Exercise ownership conversion and a synthetic platform session across both HTTP services."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
OLD_PY=ROOT/'.venv/Scripts/python.exe'
NEW_PY=ROOT/'.venv-rebuild/Scripts/python.exe'


def wait(url,timeout=45):
    deadline=time.time()+timeout
    while time.time()<deadline:
        try:
            with urlopen(url,timeout=2) as response:
                if response.status==200:return
        except Exception: time.sleep(.25)
    raise RuntimeError('Rehearsal service did not become ready.')


def command(python,args,env,cwd=ROOT):
    result=subprocess.run([str(python),*args],cwd=cwd,env=env,text=True,capture_output=True,timeout=180)
    if result.returncode: raise RuntimeError('Rehearsal command failed.')
    return result.stdout


def request(url,method='GET',body=None,token=None):
    data=json.dumps(body).encode() if body is not None else None
    headers={'Content-Type':'application/json'} if data else {}
    if token: headers['Authorization']='Bearer '+token
    with urlopen(Request(url,data=data,headers=headers,method=method),timeout=30) as response:
        return response.status,json.loads(response.read())


def run(source,platform_db,legacy_db):
    source,platform_db,legacy_db=map(lambda value:Path(value).resolve(),(source,platform_db,legacy_db))
    if not source.is_file() or platform_db.exists() or legacy_db.exists():
        raise ValueError('Source must exist and rehearsal databases must be new.')
    secret='bridge-rehearsal-secret-'+'x'*40
    confirmation='bridge-transfer-confirmation-'+'y'*40
    shutil.copy2(source,legacy_db)
    legacy_env={**os.environ,'APP_ENV':'test','DATABASE_URL':'sqlite:///'+legacy_db.as_posix(),
        'SECRET_KEY':'legacy-rehearsal-jwt-'+'z'*40,'MOVENA_INTERNAL_ASSERTION_SECRET':secret,
        'MOVENA_ALLOW_IDENTITY_OWNERSHIP_TRANSFER':'true','ENABLE_EXERCISE_RECOGNITION':'false',
        'ENABLE_ML_SECOND_OPINION':'false','ENABLE_PUBLIC_DEMO_MODE':'false'}
    command(OLD_PY,['-m','alembic','-c',str(ROOT/'alembic.ini'),'upgrade','head'],legacy_env)
    platform_db.parent.mkdir(parents=True,exist_ok=True); platform_db.touch(exist_ok=False)
    platform_env={**os.environ,'DJANGO_SETTINGS_MODULE':'movena.rehearsal_settings',
        'MOVENA_REHEARSAL_DATABASE':str(platform_db),'MOVENA_IDENTITY_MODE':'legacy',
        'MOVENA_IDENTITY_TRANSFER_CONFIRMATION':confirmation,
        'MOVENA_INTERNAL_ASSERTION_SECRET':secret,'MOVENA_LEGACY_API_URL':'http://127.0.0.1:8060'}
    manage=[str(ROOT/'services/platform/manage.py')]
    command(NEW_PY,[*manage,'migrate','--noinput','--verbosity','0'],platform_env)
    command(NEW_PY,[*manage,'import_identity_snapshot',str(source),'--persist'],platform_env)
    command(NEW_PY,[*manage,'transfer_identity_ownership',str(source),'--execute'],platform_env)
    legacy_process=subprocess.Popen([str(OLD_PY),'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8060','--no-access-log'],
        cwd=ROOT/'backend',env=legacy_env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    platform_process=None
    try:
        wait('http://127.0.0.1:8060/health')
        # The command prints aggregate counts; database state is authoritative evidence.
        command(NEW_PY,[*manage,'publish_identity_projections'],platform_env)
        synthetic_id='00000000-0000-4000-8000-000000000777'
        seed=("from django.contrib.auth.hashers import make_password; from django.utils import timezone; "
              "from identity.models import Account; from identity.outbox import request_account_projection; "
              "now=timezone.now(); a=Account.objects.create(user_id='"+synthetic_id+"',legacy_id=None,username='bridge.synthetic',"
              "email='bridge-synthetic@example.test',password_hash=make_password('Synthetic-bridge-482!'),full_name='Synthetic Patient',"
              "role='patient',is_active=True,is_verified=True,account_status='active',is_protected=False,token_version=0,"
              "permissions_json='[\"analysis:create\",\"analysis:read:own\",\"session:manage:own\"]',email_verified_at=now,created_at=now,updated_at=now,credential_owner='platform'); request_account_projection(a)")
        command(NEW_PY,[*manage,'shell','-c',seed],platform_env)
        command(NEW_PY,[*manage,'publish_identity_projections'],platform_env)
        transition_env={**platform_env,'MOVENA_IDENTITY_MODE':'transition','MOVENA_IDENTITY_TRANSFER_CONFIRMATION':''}
        platform_process=subprocess.Popen([str(NEW_PY),'-m','uvicorn','movena.asgi:application','--host','127.0.0.1','--port','8061','--no-access-log'],
            cwd=ROOT/'services/platform',env=transition_env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        wait('http://127.0.0.1:8061/health')
        status,login=request('http://127.0.0.1:8061/api/v2/auth/login','POST',
            {'email':'bridge.synthetic','password':'Synthetic-bridge-482!'})
        care_status,profile=request('http://127.0.0.1:8061/api/v2/patient/health-profile',token=login['access_token'])
        with sqlite3.connect(legacy_db) as db:
            imported=list(db.execute("SELECT identity_owner,password_hash FROM users WHERE user_id != ?",(synthetic_id,)))
            synthetic=db.execute("SELECT identity_owner,password_hash FROM users WHERE user_id=?",(synthetic_id,)).fetchone()
        verified=(status==200 and care_status==200 and imported and all(row[0]=='platform' and row[1]=='!platform-owned' for row in imported)
                  and synthetic==('platform','!platform-owned') and profile.get('patient_id'))
        return {'verified':bool(verified),'imported_accounts_converted':len(imported),
            'synthetic_login_succeeded':status==200,'delegated_care_read_succeeded':care_status==200,
            'legacy_passwords_removed':all(row[1]=='!platform-owned' for row in imported),
            'production_cutover_performed':False,'real_account_passwords_tested':False}
    finally:
        if platform_process: platform_process.terminate(); platform_process.wait(timeout=10)
        legacy_process.terminate(); legacy_process.wait(timeout=10)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('source',type=Path); parser.add_argument('platform_db',type=Path); parser.add_argument('legacy_db',type=Path); parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try: result=run(args.source,args.platform_db,args.legacy_db)
    except (ValueError,RuntimeError,TimeoutError): raise SystemExit('Two-service identity bridge rehearsal failed.') from None
    rendered=json.dumps(result,indent=2)+'\n'; print(rendered)
    if args.output: args.output.write_text(rendered,encoding='utf-8')
    raise SystemExit(0 if result['verified'] else 1)
