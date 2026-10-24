# Lumen for webOS 5 — upstream integrated

An Apple TV-inspired launcher for rooted LG webOS TVs, combining the current
[Lumen upstream](https://github.com/ammar027/lumen-webos) with the accepted webOS 5
Home grid, Inputs and Control Center design.

**`webos5-upstream` is the maintained branch.** It includes upstream Lumen 1.1.4
and all 92 build layers, then adds a small compatibility and presentation layer
under [`compat/`](compat/README.md). The previous 0.3.14 fork is archived at
[`archive/webos5-before-upstream-2026-10-24`](https://github.com/xcv58/lumen-webos/tree/archive/webos5-before-upstream-2026-10-24).

## What it includes

- A five-column app grid: Down expands it, Back collapses it. Folders and moving
  apps across rows retain focus.
- Rounded Inputs and Control Center panels with aligned glass edges, readable
  labels and a volume pill that fills brightly from the left.
- Optional immediate focus sounds on Home, Inputs and Control Center, with no
  sound queue or throttle. Opening panels, blocked moves and volume changes stay quiet.
- Daily scenic backgrounds and a photo frame with transitions, clock and captions.
- Upstream Settings, StandBy, aerials, Photos in Lumen, Immich, wallpaper library,
  app management and additional TV controls. Appearance can switch to upstream's
  Home and Control Center for comparison.
- An optional, separately installed Home/wake helper that preserves active HDMI
  inputs when a game console wakes the TV. Installing the app does not claim Home.

## Builds and installation

The [integrated build workflow](https://github.com/xcv58/lumen-webos/actions/workflows/release.yml)
produces an audited `lumen-webos5-integrated` artifact containing the IPK,
`SHA256SUMS.txt` and its package audit. Workflow builds do not publish a GitHub
release or a Homebrew feed. The older 0.3.14 release belongs to the archived fork.

Install `local.lumen.upstreamtrial_1.1.5_all.ipk` using Dev Manager Desktop or the
webOS CLI, after checking its SHA256. It appears as **Lumen Upstream Trial**.
The ID remains `local.lumen.upstreamtrial` so existing integrated-trial users keep
their app profile and Home mapping. Installing it does not remove other apps.

Public builds contain public-domain paintings, an original generic sound, Geist
and generic app fallbacks. Private icon packs, selected reference audio, personal
TV settings and actual-TV screenshots are excluded. Weather, navigation sounds
and live Homebrew app discovery start Off; turn them on explicitly in Settings.
A public build does not include the owner's private local artwork or sound.

## Compatibility and evidence

The target is webOS 5 / Chromium 68. Live installed-app discovery and privileged
TV controls require a rooted TV with [Homebrew Channel](https://www.webosbrew.org/).
Other models and firmware remain unverified.

| Check | Evidence |
| --- | --- |
| Physical TV | LG 86UN8570AUD, webOS 5.6.2-21, firmware 04.64.00; owner accepted the 1.1.5 UI, physical Home route and stable game HDMI after console wake |
| Browser checks | Grid/folders, Inputs, both-appearance volume pill, stale/failed reads, upstream feature integration, focus sounds and cleanup |
| Optional wake helper | 28 state fixtures and native HDMI preservation checks; actual console wake confirmed by owner |
| Public package | Generic cue, no private icon pack or cached photos, Chrome 68 classic bundle, license notices, no persistent Home/root service |

The physical TV uses a private local build. Public-package build/audit checks do
not claim it was installed or acoustically accepted on that TV. Exhaustive aerial,
Immich and multi-hour stability tests have not been completed.

## Build from source

Use Python 3.9+, Node 22 and npm. From a fresh checkout:

```sh
git clone https://github.com/partridgeworks/webos-launcher app
git -C app checkout 1e2c39b9a988ceb1b258e40e3592bda84a2aa076
npm ci --prefix app
python3 compat/fetch-upstream-release.py
python3 compat/build.py
python3 compat/verify-package.py app/build/local.lumen.upstreamtrial_1.1.5_all.ipk
```

The asset fetch pins both the upstream 1.1.4 release and its expected checksum.
The build resets generated `app/public/`, applies all upstream layers, adds the
accepted presentation and emits the public IPK. Keep authoring changes in
`compat/`, rather than generated `app/`. Do not use `tools/build_release.py` for
this fork; it packages upstream's separate app.

See [build and browser checks](compat/README.md), [Home/wake adoption and recovery](compat/tv/README.md),
and the [upstream pipeline reference](REBUILD.md). Home takeover is an explicit,
separate root setup; keep LG Home and Homebrew available for recovery.

## Credits

Built on [ammar027/Lumen](https://github.com/ammar027/lumen-webos) and
[partridgeworks/webos-launcher](https://github.com/partridgeworks/webos-launcher),
with contributions and ideas from Sam Renfrew's fork and lesnolie/Tigris. Code is
MIT; Geist uses the SIL Open Font License. See [third-party notices](THIRD_PARTY_NOTICES.md)
and [upstream's README](docs/UPSTREAM-README.md). Not affiliated with LG, Apple or
app vendors.
