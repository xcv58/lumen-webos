#!/usr/bin/env python3
"""Audit the public integrated IPK; never install or execute the package."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
APP_ID = 'local.lumen.upstreamtrial'


def check(package):
    payload = subprocess.check_output(['ar', '-p', str(package), 'data.tar.gz'])
    app, all_names = {}, []
    base = f'usr/palm/applications/{APP_ID}/'
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
        for entry in archive.getmembers():
            name = PurePosixPath(entry.name)
            assert not name.is_absolute() and '..' not in name.parts, 'Unsafe archive path'
            assert not entry.issym() and not entry.islnk(), 'Unexpected package link'
            if not entry.isfile():
                continue
            name = str(name)
            assert name not in all_names, 'Duplicate package file'
            all_names.append(name)
            assert name.startswith(base) or name.startswith('usr/palm/packages/'), 'Unexpected service or system file'
            if name.startswith(base):
                app[name[len(base):]] = archive.extractfile(entry).read()
    manifest = json.loads(app['appinfo.json'])
    assert manifest['id'] == APP_ID and manifest['version'] == '1.1.5'
    assert not manifest.get('appCategory'), 'Public install must not claim Home'
    assert not manifest.get('requiredPermissions'), 'Unexpected permission expansion'
    html = app['index.html'].decode()
    assert 'type="module"' not in html and './assets/app.js' in html, 'Classic bundle required'
    assert "const BROWSER_TARGET = 'chrome68'" in (ROOT / 'app/vite.config.ts').read_text()
    preparation = json.loads((ROOT / '.trial-evidence/build-preparation.json').read_text())
    assert preparation['upstreamLayersApplied'] == 92
    assert preparation['localReferenceAssets'] is False, 'Refuse a private reference build'
    storage = (ROOT / 'app/src/lib/storage.ts').read_text()
    assert 'useHomebrew: false,' in storage and 'showWeather: false,' in storage
    assert "navigationSounds:'off'" in storage
    for name, data in app.items():
        assert not name.startswith(('cache/', 'private/', 'iconpack/', 'icons/apps/')), 'Unexpected private or app artwork'
        assert not name.endswith(('.key', '.pem', '.map', '.ipk')), 'Unexpected credential or build artifact'
        for marker in [b'/Users/', b'BEGIN PRIVATE KEY', b'BEGIN OPENSSH PRIVATE KEY']:
            assert marker not in data, 'Personal device data in package'
    with tempfile.TemporaryDirectory() as directory:
        cue = Path(directory) / 'navigation-focus-v1.pcm'
        subprocess.run(['python3', str(ROOT / 'compat/generate-navigation-sound.py'), '--output', str(cue)], check=True)
        assert app['sounds/navigation-focus-v1.pcm'] == cue.read_bytes(), 'Public cue differs from generator'
        assert app['sounds/navigation-ready.pcm'] == (cue.parent / 'navigation-ready.pcm').read_bytes()
    for name in ['Geist-OFL.txt', 'Tigris-MIT.txt', 'Lumen-MIT.txt', 'preact-MIT.txt', 'LICENSE.txt']:
        assert app['licenses/' + name], 'Missing license notice: ' + name
    assert len([name for name in app if name.startswith('wallpapers/') and name.endswith('.jpg')]) == 15
    assert app['trial-idle-watch.sh'] == (ROOT / 'compat/trial-idle-watch.sh').read_bytes()
    assert not any(name.endswith('on-power.sh') or 'init.d/' in name for name in all_names)
    return {
        'package': package.name, 'packageSHA256': hashlib.sha256(package.read_bytes()).hexdigest(),
        'appId': APP_ID, 'version': manifest['version'], 'browserTarget': 'chrome68',
        'upstreamLayersApplied': 92, 'applicationFileCount': len(app),
        'classicBundle': True, 'genericCue': True, 'privateReferenceAssets': False,
        'personalDeviceDataIncluded': False, 'homeRemapperIncluded': False,
        'rootServicesIncluded': False, 'installedOnTV': False,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check(args.package.resolve())
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(encoded, end='')
