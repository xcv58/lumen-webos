# Lumen 1.1 and the webOS 5 fork

Read-only comparison on October 24, 2026. The main reference is
[Lumen 1.1.0](https://github.com/ammar027/lumen-webos/releases/tag/v1.1.0), commit
`b08131dcc8d2b1698873e729542085c1ca84dcd3`. The newer
[1.1.3 patch release](https://github.com/ammar027/lumen-webos/releases/tag/v1.1.3)
was also checked for scope. No upstream package was installed on a TV during this
comparison, and no TV settings were changed.

## Findings

| Area | Upstream 1.1 | webOS 5 preview decision |
| --- | --- | --- |
| Browser target | README specifies Chromium 79+; the published 1.1.0 IPK uses a classic deferred app script | Retain the explicit Chromium 68 JavaScript/CSS target and classic bundle. A classic entry alone does not establish full webOS 5 compatibility |
| `apply_webos5.py` | Adopts the two fixes from PR #8; its name does not indicate a complete webOS 5 port | Treat those contributions as already adopted |
| Native icons | Keeps the batch fast path, then retries missed icons in 24 KiB pieces; detects PNG/JPEG/WebP | Retain bounded reads and independent failures; our cache also includes file size and modification time |
| Input labels | Converts generic Input Source names to HDMI/AV and preserves custom labels | Keep the accepted input grid, explicit active/last-used states and unknown connection handling |
| Control Center | New grid, expanding choice lists, backlight and eye-comfort controls | Keep the accepted panels and bright-left volume pill. New TV controls need firmware-specific read/write checks before porting |
| Settings and clock | Page-stack settings, previews, clock layouts and appearance controls | Useful future candidates; assess each without replacing the accepted Home or panels |
| Screensavers | Photo source/clock controls, StandBy faces and optional Immich; 1.1.3 adds Aerials | Keep the existing bounded photo cache and foreground-only frame. Assess new sources and faces individually |
| Live/liquid glass | Optional backdrop-filter and SVG-filter effects, plus canvas backdrops | Retain the cached glass path tested on Chromium 68. New effects need feature detection and TV performance measurement |
| Recent apps | Running-app switcher and close actions | Different scope from our optional recent-history row; do not silently migrate one into the other |
| System changes | Native Home selection guidance and optional scripts; additional root-backed settings/backup features | Keep Home adoption and startup/wake outside the public package |
| Focus audio | Our optional cross-panel focus cue and readiness behavior are not among the two adopted pieces | Retain the existing Off / Soft implementation and original public cue |

The downloaded upstream 1.1.0 package matched its published checksum:
`f526f2809f831bfb9a9e7b48468e20ab2e0df0817f6322e39c88dee271d14c25`.
Its classic script is evidence against assuming a module-entry failure. This
comparison does not assert that 1.1 fails on webOS 5; it establishes that the
upstream documented target and its newer UI still need compatibility and physical
performance validation before replacing the tested fork.

The 1.1.3 patch adds Aerials, descriptions and video-wallpaper fixes. It does not
establish a tested Chromium 68 port or change the decisions above.

## Next contributions and ports

1. Keep the existing UI and publish a reproducible webOS 5 preview with generic
   assets, installation/recovery notes and explicit validation limits.
2. Evaluate small settings improvements such as Reduce motion and clock options
   in separate changes. Add hardware-facing controls only with device read-back
   tests and recovery for their settings.
3. Before sending an upstream PR, check current upstream first. Icon cache
   invalidation and stale-control-read protection are possible focused candidates,
   subject to reproducing a remaining issue. No duplicate PR is needed for the
   already adopted icon and label fixes.
4. Keep the fork link available to the maintainer. Future contributions should fit
   upstream's layout and video-wallpaper approach.

## Primary sources

- [Maintainer's scope decision](https://github.com/ammar027/lumen-webos/pull/8#issuecomment-6379246996)
- [Release-number correction](https://github.com/ammar027/lumen-webos/pull/8#issuecomment-6382804472)
- [1.1 README and compatibility statement](https://github.com/ammar027/lumen-webos/blob/v1.1.0/README.md)
- [Two adopted fixes](https://github.com/ammar027/lumen-webos/blob/v1.1.0/tools/apply_webos5.py)
- [Control Center adaptation](https://github.com/ammar027/lumen-webos/blob/v1.1.0/tools/apply_controlcenter.py)
- [Additional options and root-backed behavior](https://github.com/ammar027/lumen-webos/blob/v1.1.0/tools/apply_moreoptions.py)
- [Optional live glass](https://github.com/ammar027/lumen-webos/blob/v1.1.0/tools/apply_liveglass.py)
