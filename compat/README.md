# Upstream-first webOS 5 experiment

This branch starts at upstream Lumen v1.1.4, commit
`a85b99a4a415b4f2fff5e09d50c85ce950a0504f`. It retains upstream's complete
92-layer build and UI. The maintained `webos5` fork and the accepted TV launcher
remain separate while this approach is evaluated.

## Build

Use Python 3.9+ and upstream's Node/npm toolchain. Prepare `app/` following
the upstream rebuild instructions, pinned to the original launcher commit
`1e2c39b9a988ceb1b258e40e3592bda84a2aa076`, and install its npm dependencies.
Place the official v1.1.4 release IPK and its published `SHA256SUMS.txt` in
`../lumen-upstream-first-evidence/upstream-release/`.

Run `python3 compat/build.py` from the repository root. This resets the
generated app's tracked source, manifest, index and Vite config, applies all
upstream layers, applies the small compatibility layer, and builds the package.
Keep edits in the upstream scripts or `compat/`, rather than in generated `app/`.
The output is `app/build/local.lumen.upstreamtrial_1.1.4_all.ipk`.

`run-layer.py` substitutes upstream's hardcoded developer path in memory.
It leaves the upstream scripts on disk unchanged. The build follows upstream's
documented allowance for the already-applied `apply_dockhide` edit.

## Compatibility and trial isolation

- Compile JS and CSS for Chrome 68; keep upstream's classic script bundle.
- Use app ID `local.lumen.upstreamtrial` and title **Lumen Upstream Trial**.
  Remove the native Home category and isolate backup/marker paths under
  `/tmp/lumen-upstreamtrial`. No Home watcher or startup service is installed.
- Route sleep-timer reads and writes through the existing Homebrew root bridge.
  On the tested webOS 5 TV, upstream's direct web-app request fails, while the
  root request succeeds. Validate timer choices and check the native response.
  Reads combine the separate remaining-minute and remaining-second fields,
  while also handling a seconds-only response.
- Protect both the accepted launcher and candidate from the app's uninstall menu.
- Start weather Off. Use artwork and licenses from the checksummed official
  public package; do not copy private fonts, photos, audio or TV preferences.

The only runtime behavior fix discovered so far is the sleep-timer bridge.
Identity/path changes isolate the experiment; they are not evidence of upstream
UI incompatibility. The base launcher commit is the same as the maintained fork.

## Initial device results

Tested on an LG 86UN8570AUD, webOS 5.6.2-21, firmware 04.64.00,
Chrome 68.0.3440.106. The complete upstream UI launches and renders.
Automated native checks passed for onboarding, app discovery, Down/Back between
app rows, Inputs movement/Back, Control Center's Sound list, Settings, local
photo slideshow changes and exit, and StandBy Digital/Analog movement and exit.
The backlight slider changed the actual TV value and the baseline was restored.
The corrected sleep timer set 60 minutes on the real TV, remained at 60 minutes
after reopening Control Center, and was cancelled after the check.

Final preservation checks matched the accepted app's manifest, bundle, audio
cue, configuration, Home mapping and startup-hook hashes against the fresh
pre-install snapshot. Volume, sound, picture, backlight and global screensaver
settings matched; the sleep timer was Off. Both apps could be launched, and the
candidate's installed bundle matched the production build. The accepted app
remains the Home/startup target. The maintained fork checkout stayed clean at
`2e38e071c0d531d8244c4001250e278d5aa8ab22`.

Final candidate IPK SHA256:
`79ee75ef53348af3796a9d9409078ffa3137ae1e287c1d59c66731a47c169f09`.
Temporary transfer files were confined to `/tmp`; the restricted package server
closed after its 90-second limit and the local browser preview was stopped.

The desktop production preview also passed onboarding, row navigation, Inputs
and Control Center with no page exceptions. Upstream's five Python checks and
startup readiness suite passed. Optional private SF font requests fail because
those files are intentionally absent; the packaged fallback font renders.

Physical remote feel and owner visual acceptance remain separate from these
automated checks. Video/aerial streaming, Immich, every sound/picture mode,
clock face, idle timing and long-running stability have not been exhaustively
tested. No full standby/reboot or default-Home experiment is needed at this stage.

## Differences to assess before adoption

| Area | Upstream-first candidate | Accepted launcher |
| --- | --- | --- |
| Apps below dock | Upstream scrolling app rows | Custom expanding app grid |
| Inputs and Control Center | Current upstream glass and animations | Accepted panel contrast, borders and corners |
| Volume | Remote volume buttons; panel has Backlight | Accepted volume pill in Control Center |
| Focus feedback | Upstream behavior | Accepted immediate sounds on Home and panels |
| Photos/backgrounds | Upstream library, local photos, StandBy and aerial options | Accepted daily-photo/background implementation |
| Startup and Home | Separate manually launched candidate | Existing approved Home mapping and wake helper |

Detailed native snapshots and TV screenshots stay outside this repository in
the private evidence directory. They must not be included in public commits.
Do not change the accepted app's identity, preferences or Home hooks to promote
this candidate until the owner has evaluated the differences.
