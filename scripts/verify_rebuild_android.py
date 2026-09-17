"""Check the compiled debug package and merged dependency manifest after a build.

This is packaging evidence only: it cannot verify devices or release signing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ANDROID = '{http://schemas.android.com/apk/res/android}'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify():
    native = ROOT / 'apps/native'
    apk = native / 'build/app/outputs/flutter-apk/app-debug.apk'
    manifest = native / 'build/app/intermediates/merged_manifests/debug/processDebugManifest/AndroidManifest.xml'
    tree = ET.parse(manifest).getroot()
    require(tree.get('package') == 'ai.movena.mobile.development', 'Unexpected debug application identifier')
    permissions = {node.get(ANDROID + 'name') for node in tree.findall('uses-permission')}
    require('android.permission.RECORD_AUDIO' not in permissions, 'A dependency restored microphone access')
    require({'android.permission.CAMERA', 'android.permission.INTERNET'} <= permissions, 'Required capture/network permissions missing')
    features = {node.get(ANDROID + 'name'): node.get(ANDROID + 'required', 'true') for node in tree.findall('uses-feature')}
    for camera in ['android.hardware.camera.any', 'android.hardware.camera', 'android.hardware.camera.autofocus']:
        require(features.get(camera) == 'false', 'Camera hardware became mandatory: ' + camera)
    require(any(node.get(ANDROID + 'scheme') == 'movena' for node in tree.findall('.//intent-filter/data')), 'Retained account link scheme missing')
    application = tree.find('application')
    require(application is not None, 'Application manifest missing')
    require(application.get(ANDROID + 'debuggable') == 'true', 'Expected a debug package')
    resources = native / 'android/app/src/main/res/xml'
    for attribute, filename, sections in [
        ('fullBackupContent', 'backup_rules', ['.']),
        ('dataExtractionRules', 'data_extraction_rules', ['cloud-backup', 'device-transfer']),
    ]:
        require(application.get(ANDROID + attribute) == '@xml/' + filename, 'Backup manifest reference missing')
        rule = ET.parse(resources / (filename + '.xml')).getroot()
        for section in sections:
            node = rule if section == '.' else rule.find(section)
            require(node is not None, 'Backup transfer policy missing')
            includes = [(child.get('domain'), child.get('path')) for child in node.findall('include')]
            require(includes == [('sharedpref', 'FlutterSharedPreferences.xml')], 'Backup must include only locale/theme preferences')
    with ZipFile(apk) as archive:
        files = archive.namelist()
        require({'res/xml/backup_rules.xml', 'res/xml/data_extraction_rules.xml'} <= set(files), 'Compiled backup resources missing')
        abis = sorted({name.split('/')[1] for name in files if name.startswith('lib/') and name.endswith('/libflutter.so')})
        require(set(abis) == {'arm64-v8a', 'armeabi-v7a', 'x86_64'}, 'Expected all supported debug ABIs')
    with apk.open('rb') as artifact:
        digest = hashlib.file_digest(artifact, 'sha256').hexdigest()
    properties = (native / 'android/local.properties').read_text(encoding='utf-8')
    sdk_match = re.search(r'^sdk\.dir=(.+)$', properties, re.MULTILINE)
    sdk = Path(os.environ.get('ANDROID_HOME') or (sdk_match.group(1).replace('\\:', ':').replace('\\\\', '\\') if sdk_match else ''))
    signers = sorted((sdk / 'build-tools').glob('*/apksigner.bat'), reverse=True)
    require(bool(signers), 'Android apksigner was not found')
    signed = subprocess.run([str(signers[0]), 'verify', '--verbose', '--print-certs', str(apk)],
                            capture_output=True, text=True, check=False)
    require(signed.returncode == 0, 'APK signature verification failed')
    signature_text = signed.stdout + signed.stderr
    require('Verified using v2 scheme (APK Signature Scheme v2): true' in signature_text,
            'APK Signature Scheme v2 is required')
    certificate = re.search(r'Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]+)', signature_text)
    require(certificate is not None, 'APK signing certificate digest is missing')
    require('CN=Android Debug' in signature_text, 'Expected an Android Debug certificate')
    return {
        'artifact': str(apk.relative_to(ROOT)).replace('\\', '/'),
        'sha256': digest,
        'size_bytes': apk.stat().st_size,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'package': tree.get('package'), 'version_name': tree.get(ANDROID + 'versionName'),
        'version_code': tree.get(ANDROID + 'versionCode'), 'abis': abis,
        'microphone_permission': False, 'camera_hardware_required': False,
        'backup_policy': 'locale/theme preferences only', 'real_device_tested': False,
        'release_signing_verified': False,
        'signature_verification': {'scheme': 'v2', 'certificate_kind': 'Android Debug',
                                   'certificate_sha256': certificate.group(1).lower()},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    evidence = json.dumps(verify(), indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(evidence, encoding='utf-8')
    print(evidence)
