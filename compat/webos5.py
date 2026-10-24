"""Small, evidence-driven patches applied after the untouched upstream layers."""
from pathlib import Path


def replace_once(source: str, before: str, after: str) -> str:
    assert source.count(before) == 1, f'Upstream changed: {before[:100]}'
    return source.replace(before, after, 1)


def apply(app: Path) -> list[str]:
    path = app / 'src/lib/tvcontrols.ts'
    source = path.read_text()
    source = replace_once(source,
        "const sleep = lunaCall<{sleepTimeSecond?: number}>(SLEEP + 'getRemainTime', {}).then((r) => {\n\t\tconst minutes = Math.ceil((Number(r.sleepTimeSecond) || 0) / 60);",
        "const sleep = root(\"luna-send -w 4000 -n 1 \" + SLEEP + \"getRemainTime '{}'\").then((text) => {\n\t\tconst r = JSON.parse(text) as {sleepTimeSecond?: number; sleepTimeMinute?: number};\n\t\tconst minutes = Math.ceil(((Number(r.sleepTimeMinute) || 0) * 60 + (Number(r.sleepTimeSecond) || 0)) / 60);")
    source = replace_once(source,
        "return lunaCall(SLEEP + 'add', {sleepTimeMinute: minutes}).then(() => undefined);",
        "if (SLEEP_MINUTES.indexOf(minutes) === -1) return Promise.reject(new Error('unknown sleep timer'));\n\treturn root(\"luna-send -w 4000 -n 1 \" + SLEEP + \"add '\" + JSON.stringify({sleepTimeMinute: minutes}) + \"'\").then((text) => {\n\t\tconst r = JSON.parse(text) as {returnValue?: boolean; errorText?: string};\n\t\tif (r.returnValue !== true) throw new Error(r.errorText || 'sleep timer refused');\n\t});")
    path.write_text(source)

    # Keep the accepted app and this candidate out of upstream's uninstall action.
    path = app / 'src/lib/root.ts'
    source = replace_once(path.read_text(),
        'const KEEP_INSTALLED = /^(com\\.ammar027',
        'const KEEP_INSTALLED = /^(local\\.lumen\\.(trial|upstreamtrial)$|com\\.ammar027')
    path.write_text(source)
    return ['src/lib/tvcontrols.ts', 'src/lib/root.ts']
