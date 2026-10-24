#!/usr/bin/env python3
"""Fetch the pinned public upstream assets without downloading personal assets."""
import argparse
import hashlib
from pathlib import Path
import urllib.request

NAME = 'com.ammar027.lumen_1.1.4_all.ipk'
SHA256 = 'ba56dd6499eab4cea1582db904b9de1cdd89c01ec12338a9a14f139783516605'
BASE = 'https://github.com/ammar027/lumen-webos/releases/download/v1.1.4/'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parents[1] / '.cache/upstream-release')
args = parser.parse_args()
args.directory.mkdir(parents=True, exist_ok=True)
for name in [NAME, 'SHA256SUMS.txt']:
    target = args.directory / name
    if not target.exists():
        request = urllib.request.Request(BASE + name, headers={'User-Agent': 'lumen-webos-build'})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
        if name == NAME:
            assert hashlib.sha256(data).hexdigest() == SHA256, 'Upstream IPK checksum mismatch'
        temp = target.with_name(target.name + '.download')
        temp.write_bytes(data)
        temp.replace(target)
assert hashlib.sha256((args.directory / NAME).read_bytes()).hexdigest() == SHA256
assert f'{SHA256}  {NAME}' in (args.directory / 'SHA256SUMS.txt').read_text()
print(f'Verified pinned upstream release {NAME}: {SHA256}')
