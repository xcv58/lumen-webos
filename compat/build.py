#!/usr/bin/env python3
"""Build upstream's current pipeline, then add the isolated Chromium 68 candidate patch."""
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
from webos5 import apply as apply_webos5

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app'
EVIDENCE = ROOT.parent / 'lumen-upstream-first-evidence'
APP_ID = 'local.lumen.upstreamtrial'
PIN = '1e2c39b9a988ceb1b258e40e3592bda84a2aa076'
UPSTREAM_COMMIT = 'a85b99a4a415b4f2fff5e09d50c85ce950a0504f'


def run(*args, cwd=APP):
    subprocess.run([str(arg) for arg in args], cwd=cwd, check=True)


def layer(name):
    run(sys.executable, ROOT / 'compat/run-layer.py', ROOT / 'tools' / name)


assert subprocess.check_output(['git', '-C', str(APP), 'rev-parse', 'HEAD'], text=True).strip() == PIN
run('git', 'merge-base', '--is-ancestor', UPSTREAM_COMMIT, 'HEAD', cwd=ROOT)
run('git', 'checkout', '--', 'src', 'index.html', 'public/appinfo.json', 'vite.config.ts')
shutil.copytree(ROOT / 'app-assets/public', APP / 'public', dirs_exist_ok=True)
layer('build_catalog.py')
layer('build_iconpack.py')
block = (ROOT / 'REBUILD.md').read_text().split('```sh', 1)[1].split('```', 1)[0].replace('\\\n', ' ')
names = re.findall(r'apply_[a-z0-9_]+', re.search(r'for s in (.*?); do', block, re.S).group(1))
for name in names:
    try:
        layer(name + '.py')
    except subprocess.CalledProcessError:
        if name != 'apply_dockhide':
            raise
        # Only tolerate upstream's known final watcher assertion. Earlier
        # failures must not silently produce a partially applied UI layer.
        assert 'dockHidden: boolean;' in (APP / 'src/screens/Home.tsx').read_text()
        assert 'setVideoFlag(config.videoWallpaper)' in (APP / 'src/app.tsx').read_text()
        assert '.rows--hidden' in (APP / 'src/theme/global.css').read_text()
        assert 'VIDEO_FLAG=/var/lib/homehook/video-wallpaper' in (ROOT / 'tools/tv/watch.sh').read_text()
        print('Same upstream exception: the tracked watcher edit may already be applied.')

# Keep upstream's UI. These are compatibility/identity/isolation changes only.
runtime_compat = apply_webos5(APP)
vite = APP / 'vite.config.ts'
source = vite.read_text()
assert "const BROWSER_TARGET = 'chrome79'" in source
vite.write_text(source.replace("const BROWSER_TARGET = 'chrome79'", "const BROWSER_TARGET = 'chrome68'"))
changed = []
for path in (APP / 'src').rglob('*'):
    if path.suffix not in ['.ts', '.tsx', '.css']:
        continue
    before = path.read_text()
    after = re.sub(r'com\.ammar027\.lumen(?![A-Za-z0-9_.])', APP_ID, before)
    after = after.replace('/var/lib/homehook', '/tmp/lumen-upstreamtrial')
    after = after.replace('touch /tmp/allow_lg_home', 'mkdir -p /tmp/lumen-upstreamtrial && touch /tmp/lumen-upstreamtrial/allow_lg_home')
    if path.name == 'storage.ts':
        after = after.replace('showWeather: true,', 'showWeather: false,')
    if after != before:
        path.write_text(after)
        changed.append(str(path.relative_to(APP)))
manifest_path = APP / 'public/appinfo.json'
manifest = json.loads(manifest_path.read_text())
manifest.update(id=APP_ID, title='Lumen Upstream Trial', vendor='Local compatibility experiment', inspectable=True)
manifest.pop('appCategory', None)
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')

# Use only the publicly released artwork/licences, with its published checksum.
release = EVIDENCE / 'upstream-release/com.ammar027.lumen_1.1.4_all.ipk'
digest = hashlib.sha256(release.read_bytes()).hexdigest()
assert digest in (release.parent / 'SHA256SUMS.txt').read_text()
payload = subprocess.check_output(['ar', '-p', str(release), 'data.tar.gz'])
public_assets = []
with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
    prefix = 'usr/palm/applications/com.ammar027.lumen/'
    for entry in archive.getmembers():
        name = entry.name.removeprefix('./')
        if not entry.isfile() or not name.startswith(prefix):
            continue
        relative = Path(name[len(prefix):])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe release path')
        if relative.parts[0] in ['wallpapers', 'licenses']:
            destination = APP / 'public' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.extractfile(entry).read())
            public_assets.append(str(relative))
wallpapers = [
 'View of Lake Pepin, Minnesota - Robert S. Duncanson',
 'View near Newport - John Frederick Kensett',
 'Sunset on the River Oise - Charles-Francois Daubigny',
 'Landscape - Jasper F. Cropsey', 'Corn Fields - Felix Vallotton'
]
path = APP / 'src/config/wallpapers.ts'
source = path.read_text()
source, count = re.subn(r'export const LOCAL_WALLPAPERS: LocalWallpaper\[\] = \[.*?\n\];',
 'export const LOCAL_WALLPAPERS: LocalWallpaper[] = ' + json.dumps([{'title': title, 'file': f'wallpapers/default-{i}.jpg'} for i, title in enumerate(wallpapers)], indent=1) + ';', source, flags=re.S)
assert count == 1
path.write_text(source)
EVIDENCE.mkdir(exist_ok=True)
(EVIDENCE / 'build-preparation.json').write_text(json.dumps({
 'upstreamCommit': UPSTREAM_COMMIT,
 'launcherBase': PIN, 'upstreamLayersApplied': len(names), 'appId': APP_ID,
 'browserTarget': 'chrome68', 'compatibilityChangedSourceFiles': changed,
 'runtimeCompatibilityFiles': runtime_compat,
 'publicReleaseSHA256': digest, 'publicAssets': public_assets,
 'homeCategoryRemoved': True, 'sharedBackupPathsIsolated': True,
}, indent=2) + '\n')
run('npm', 'run', 'build')
run('npm', 'run', 'package')
