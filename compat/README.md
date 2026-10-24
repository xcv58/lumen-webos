# Upstream Lumen with the accepted webOS 5 presentation

The separate **Lumen Upstream Trial 1.1.5** now carries the accepted Home grid,
Inputs and Control Center surfaces, volume pill, focus feedback, cached daily
backgrounds and photo frame. It starts from upstream Lumen v1.1.4 at
`a85b99a4a415b4f2fff5e09d50c85ce950a0504f` and applies all 92 upstream layers.
The upstream scripts are unchanged; the presentation is a readable module layer.
The maintained `webos5` fork and the previous accepted build remain available
separately. After acceptance, the two obsolete Lumen apps were removed from the TV.

## What matches

- Five-column expanding app grid; Down expands and Back collapses. Moving apps
  across rows and folders retains focus. Recent history is independent of whether
  a Recent row is displayed.
- Shared rounded Inputs and Control Center surfaces, including the accepted
  border-box tint, padding-box wallpaper alignment, uniform corners and soft
  upper-edge highlight. Long text stays inside its controls.
- The accepted volume pill: bright fill on the left, subdued transparent empty
  area on the right, a separate focus rim, and clipped text/icon contrast. Shape
  and layout are unchanged.
- Immediate Home, Inputs, Control Center and choice-list focus cues, one shared
  low-level keepalive, quiet boundaries/hover/opening/Back/volume changes, and
  cleanup for Off, background and photo-frame mode. No TV audio settings are
  changed by the sound module.
- Cached Bing scenic backgrounds, optional SFW collection, gradients and the
  accepted in-app photo frame with clock, captions, crossfades and pan/zoom.
  Cache files and idle handling belong only to the candidate.

Upstream Settings keeps its newer stacked pages. More TV controls and App switcher
are available in Settings > System. Upstream StandBy, Photos in Lumen, aerials,
wallpaper library and Immich implementation remain. Settings > Appearance >
Matched Home and panels can switch back to the upstream presentation. Options
that only affect upstream's flexible Home composition are hidden while the fixed
accepted composition is selected. Screensaver type can select either the matched
photo frame or an upstream screensaver.

## Structure and build

`ui/` contains the accepted presentation modules from the maintained fork at
`2e38e071c0d531d8244c4001250e278d5aa8ab22`, retaining the project's MIT licensing.
Shared app state, settings, app management and upstream screen implementations
remain upstream. `presentation.py` connects the modules after the upstream build;
`scope-css.mjs` scopes accepted styles and tokens to their own layer. Separate
panel modifiers prevent upstream's panel-reset rules from leaking into these
surfaces. The shared keyboard listener and StandBy's listener install during the
layout commit, correcting a first-key race found by the integration checks.

Use Python 3.9+, Node/npm and upstream's toolchain. Prepare `app/` as in the
upstream rebuild instructions, pinned to launcher commit
`1e2c39b9a988ceb1b258e40e3592bda84a2aa076`, and install its npm dependencies.
Place the official v1.1.4 IPK and its published `SHA256SUMS.txt` in
`../lumen-upstream-first-evidence/upstream-release/`. Then run:

```sh
python3 compat/build.py
```

This regenerates `app/`, applies all upstream layers, applies compatibility and
presentation changes, and emits
`app/build/local.lumen.upstreamtrial_1.1.5_all.ipk`. Keep authoring changes in
`compat/`, rather than in generated `app/`. `run-layer.py` substitutes upstream's
hardcoded developer directory in memory; the known already-patched watcher
assertion is tolerated only when its expected UI and watcher markers are present.

Ordinary builds use the original generated generic cue. The owner's local build
uses `--local-reference`, which reads the selected PCM and icon pack from the
private evidence directory. Local assets, TV preferences, connection helpers,
credentials and actual TV screenshots are never source or public release assets.
The local build's app order and photo cache are copied separately into only the
candidate's profile on the TV. Public build defaults do not contain owner data.

## webOS 5 and isolation

The JavaScript/CSS target is Chrome 68, retaining upstream's classic script.
Sleep timer reads/writes use the existing Homebrew bridge, validate values and
combine the TV's remaining-minute and remaining-second fields. Controls confirm
writes, retain unknown values on failed reads, reject stale responses and filter
picture/sound modes against the TV's descriptions.

The candidate ID is `local.lumen.upstreamtrial`; its native Home category is
removed. Backup/flag/idle state is under `/tmp/lumen-upstreamtrial`, and photo
files are in its own app directory. It installs no persistent Home/startup
service. Both accepted Trial and this candidate are protected from the uninstall
menu. After the owner's separate request to make testing easier, the existing
Home mapping was pointed at `local.lumen.upstreamtrial`, and its private wake
helper was replaced with `tv/on-power.sh`. This adoption is separate from the
IPK; building or installing the app does not claim Home.

The wake helper only replaces a launcher screen after eight seconds of safe
foreground observations. HDMI inputs and other apps cancel the entire wake
attempt. CEC, unknown wake reasons and failed reason reads also prevent launch;
foreground read errors wait only within a bounded window. Power, wake reason and
foreground are checked again just before launch. Screen Off and Screen Saver
never request a launcher. Pressing Home is independent of these checks and
opens the new trial immediately. A remote power-on that resumes HDMI therefore
keeps HDMI selected too; Home remains the explicit way to open the trial.

LG Home and the previous hook configuration are retained for recovery. The old
Lumen installers and earlier preferences remain in private local backups; the old
apps are no longer installed on the TV. See `tv/README.md` for the adoption policy
and rollback boundaries.

## Verification

Install test dependencies with `npm --prefix compat/tests ci` and install
Playwright's Chromium, or set `CHROMIUM_PATH` to an existing browser. Serve the
candidate production `app/dist` on localhost port 5191. The adapted checks are:

```sh
TRIAL_URL=http://127.0.0.1:5191 node compat/tests/panel-tests.mjs
TRIAL_URL=http://127.0.0.1:5191 node compat/tests/grid-edit-tests.mjs
TRIAL_URL=http://127.0.0.1:5191 node compat/tests/upstream-integration-tests.mjs
```

The navigation-sound suite uses a Vite preview on port 5193 because it also
inspects the source module. For the reference comparison, serve the accepted
0.3.13 build (or the maintained 0.3.14 build with the same UI) on port 5192 and run
`node compat/tests/match-tests.mjs`. The comparison uses identical synthetic
preferences, fixed time and the same painting; external requests are blocked.
Evidence is written under ignored `.trial-evidence/`.

Browser checks passed for accepted geometry/colors, grid editing/folders, input
state and focus restoration, both-appearance volume rendering at 0/25/50/75/100,
stale/failed reads, rapid focus feedback, native audio fixtures and keepalive
cleanup. Upstream controls/style switching and StandBy navigation also passed.
The five upstream Python checks and startup readiness suite passed.

`node compat/tests/wake-helper-tests.mjs` exercises the separate optional wake
helper. Its 28 cases cover all four HDMI inputs, AV, delayed CEC switching, late
changes immediately before launch, unknown/failed status reads, bounded retries,
standby/suspend gaps and intentional display modes. These fixtures do not replace
a physical console-wake test.

Real-TV checks use LG 86UN8570AUD, webOS 5.6.2-21, firmware 04.64.00, Chrome 68.
The installed 1.1.5 bundle and selected cue hashes matched. Native checks passed
for Home/grid, Inputs and Control Center geometry and text bounds, the live volume
fill with retained focus, choice/input return focus and the photo frame's consumed
wake key. Twelve rapid Home moves dispatched twelve successful native cues, with
measured JS dispatch delays of 0.7–4.8 ms. Inputs and Control Center shared one
keepalive, which stopped for the photo frame and resumed silently afterward.
At the UI installation checkpoint, the accepted bundle, cue, config, Home mapping
and startup hooks matched their fresh pre-install snapshot; original volume,
picture, sound and global screensaver settings were preserved. The later explicit
default adoption changes only Home's target and the private wake helper, retaining
the previous app and its recovery route. The maintained fork checkout remains
separate from this experiment.

After owner acceptance, cleanup removed only Lumen 1.0.9 (`com.ammar027.lumen`)
and Lumen Trial 0.3.13 (`local.lumen.trial`). App registrations and installation
directories were absent afterward. The remaining app IDs exactly matched the
pre-cleanup inventory minus those two. The accepted 1.1.5 bundle, preferences,
Home mapping, wake guard, audio settings and startup entries were unchanged.
LG Home, Homebrew Channel and LG Input Hook remain installed. The old installers
are kept privately on the Mac; no app or setting was republished during cleanup.

The installed local candidate IPK SHA256 is
`6544df362820665ce7cfce6ccf0f6d99ed6139426595de8b01e2ce6807acf20a`.
This local package contains the owner's selected cue/artwork and is not a public
release asset. Detailed device evidence remains outside Git.

On 2026-10-24, the owner confirmed that the updated UI looks correct, the physical
Home button opens this launcher, and the game HDMI input remains stable when the
console wakes the TV. This is now the accepted default trial setup on that TV.
Physical listening was not separately reported in that confirmation. A full
ten-minute idle test and exhaustive aerial/Immich or multi-hour stability checks
are outside this trial.
