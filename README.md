# Lumen for webOS 5

A webOS 5 / Chromium 68 launcher preview with a five-column app grid, Inputs,
Control Center, a photo frame and optional focus sounds. This fork continues the
trial from [Lumen PR #8](https://github.com/ammar027/lumen-webos/pull/8).

**[Download preview 0.3.14](https://github.com/xcv58/lumen-webos/releases/tag/webos5-v0.3.14)**
· [Install and recovery](docs/INSTALL-WEBOS5.md)
· [Build and tests](trial/README.md)
· [Comparison with Lumen 1.1](docs/UPSTREAM-1.1-COMPARISON.md)

This is an experimental fork of [ammar027/Lumen](https://github.com/ammar027/lumen-webos),
built on [partridgeworks/webos-launcher](https://github.com/partridgeworks/webos-launcher).
Upstream Lumen remains the project for its newer-TV layout and release pipeline.

## Preview

| Home | Expanded app grid |
| --- | --- |
| ![Home with generated cards](docs/trial/home.png) | ![Five-column grid](docs/trial/grid.png) |
| **Inputs** | **Control Center** |
| ![Inputs with demo values](docs/trial/inputs.png) | ![Focused volume pill at 50](docs/trial/control-center.png) |

[Full gallery, light appearance and photo frame](trial/README.md).
Screenshots use synthetic preferences, a fixed clock and generated artwork.
Public builds contain generated text cards, abstract backgrounds and an original
generic sound. Optional native icons are read from the user's own TV.

## What it does

- Down expands a five-column grid; Back collapses it. Folders and app moving remain
  available, with optional Recent visibility.
- Large PNG, JPEG and WebP native icons are read in bounded chunks. One failed icon
  does not discard the other icons.
- Inputs show AV/HDMI names, custom labels, connection state and distinct active
  versus last-used indications.
- Control Center offers sound, picture, sleep, audio and photo-frame choices, with
  confirmed settings and protection against stale replies. The volume pill fills
  brightly from the left and retains a separate focus rim.
- The in-app photo frame offers transitions, captions, a clock and consumed wake
  keys. Scenic Bing and optional SFW Wallhaven collections use bounded caching.
- Off / Soft focus sounds cover Home, Inputs and Control Center. Navigation sounds,
  live app discovery and weather start Off on a fresh install.

## Compatibility and validation

The target is webOS 5 with Chromium 68. Full app discovery, native icons and some
TV controls require a rooted TV with [Homebrew Channel](https://www.webosbrew.org/).
Enable “Live app list via Homebrew Channel” in Settings → Options for app discovery;
privileged controls use the existing Homebrew service when invoked.

| Evidence | Scope |
| --- | --- |
| Physical TV baseline | LG 86UN8570AUD, webOS 5.6.2-21, firmware 04.64.00; accepted 0.3.13 UI, remote navigation, quick controls and photo frame |
| Public 0.3.14 preview | Same UI, generic assets, fresh-install privacy defaults; production build, package checks and browser fixtures |
| Separate local setup | Home mapping, reboot launch, standby/wake and LG Home return were accepted on that TV; those root hooks are not in this package |

Other models and firmware are unverified. The public generic sound has browser
coverage; physical listening acceptance used a private local sound override.
The ten-minute idle test and multi-hour slideshow were not completed. The preview
is not installed automatically on an existing TV.

## Install or build

Install `local.lumen.trial_0.3.14_all.ipk` from the preview release with Dev Manager
Desktop or the webOS CLI. Verify it against `SHA256SUMS.txt` first. The app appears
as **Lumen webOS 5** and uses app ID `local.lumen.trial`.

Installation leaves the original Lumen app and LG Home installed. It does not map
Home, install a root service or change startup/wake hooks, clock, hosts or LG's
global screensaver timer. Existing trial users should read the update and recovery
notes because this package uses the same trial app ID.

```sh
python3 trial/prepare.py
npm --prefix app ci
npm --prefix app run build
npm --prefix app run package
python3 trial/verify-package.py app/build/local.lumen.trial_0.3.14_all.ipk
```

The preparation command pins the launcher base, applies the readable source overlay
and generates public assets. It refuses to overwrite an existing `app/`. The older
upstream patch pipeline remains under [REBUILD.md](REBUILD.md); this fork's preview
uses `trial/prepare.py` instead.

## Upstream contributions

Lumen 1.1 independently adopted the chunked-icon fallback and clearer generic
input labels from PR #8. Future contributions should be small fixes that fit
upstream; this fork keeps the webOS 5 Home, panels and audio implementation.
See the [comparison and follow-up candidates](docs/UPSTREAM-1.1-COMPARISON.md).

## Credits

Thanks to ammar027 for Lumen, the partridgeworks/webos-launcher contributors, and
lesnolie/Tigris for the glass-edge rendering reference adapted under MIT.
The typeface is Geist under the SIL Open Font License. See
[third-party notices](THIRD_PARTY_NOTICES.md) and [MIT licence](LICENSE).
This project is not affiliated with LG, Apple or any app vendor.
