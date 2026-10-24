#!/usr/bin/env python3
"""Run an upstream build layer with its fixed project path redirected locally."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
script = Path(sys.argv[1]).resolve()
assert script.is_relative_to(root / 'tools') and script.suffix == '.py'
source = script.read_text().replace('~/Developer/webos-launcher-tvos', root.as_posix())
sys.argv = [str(script), *sys.argv[2:]]
exec(compile(source, str(script), 'exec'), {'__name__': '__main__', '__file__': str(script)})
