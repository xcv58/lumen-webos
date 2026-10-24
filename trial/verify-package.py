#!/usr/bin/env python3
"""Check a public preview IPK without installing or executing it."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def check(package):
    payload = subprocess.check_output(['ar', '-p', str(package), 'data.tar.gz'])
    files = {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
        for entry in archive.getmembers():
            name = PurePosixPath(entry.name)
            assert not name.is_absolute() and '..' not in name.parts, 'Unsafe archive path'
            assert not entry.issym() and not entry.islnk(), 'Unexpected package link'
            if entry.isfile():
                files[str(name)] = archive.extractfile(entry).read()
    base = 'usr/palm/applications/local.lumen.trial/'
    app = {name[len(base):]: data for name, data in files.items() if name.startswith(base)}
    assert app and all(name.startswith(base) or name.startswith('usr/palm/packages/') for name in files), 'Unexpected service or system files'
    manifest = json.loads(app['appinfo.json'])
    expected = json.loads((ROOT / 'trial/overlay/public/appinfo.json').read_text())
    assert manifest == expected, 'App manifest differs from the source overlay'
    html = app['index.html'].decode()
    assert '<script defer src="./assets/app.js"></script>' in html
    assert 'type="module"' not in html, 'The installed app must use a classic script'
    assert 'chrome68' in (ROOT / 'trial/overlay/vite.config.ts').read_text()
    cue = app['sounds/navigation-focus-v1.pcm']
    assert cue == (ROOT / 'trial/overlay/public/sounds/navigation-focus-v1.pcm').read_bytes(), 'Public cue must match tracked generic asset'
    for name in app:
        assert not name.startswith(('cache/', 'private/', 'icons/apps/')), 'Unexpected private or third-party app asset'
        assert not name.endswith(('.key', '.pem', '.map')), 'Unexpected credential or source map'
    from assets import generate_assets
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        generated = Path(directory)
        generate_assets(generated)
        wanted = {str(p.relative_to(generated / 'public')): p.read_bytes() for p in (generated / 'public').rglob('*.svg')}
        actual = {name: data for name, data in app.items() if name.startswith(('iconpack/', 'wallpapers/'))}
        assert actual == wanted, 'Cards and wallpapers must be generated public assets'
    for name in ['Geist-OFL.txt', 'Lumen-MIT.txt', 'Tigris-MIT.txt', 'LICENSE.txt']:
        assert app['licenses/' + name], 'Missing licence: ' + name
    source = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    return {
        'package': package.name, 'packageSHA256': hashlib.sha256(package.read_bytes()).hexdigest(),
        'sourceCommit': source, 'appId': manifest['id'], 'version': manifest['version'],
        'browserTarget': 'chrome68', 'classicBundle': True,
        'genericCueSHA256': hashlib.sha256(cue).hexdigest(), 'generatedAssetCount': len(wanted),
        'applicationFileCount': len(app), 'rootServicesIncluded': False,
        'homeRemapperIncluded': False, 'personalDeviceDataIncluded': False,
        'physicalBaseline': '0.3.13 UI on LG 86UN8570AUD, webOS 5.6.2-21 / firmware 04.64.00',
        'publicPackageInstalledOnTv': False,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check(args.package.resolve())
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end='')
