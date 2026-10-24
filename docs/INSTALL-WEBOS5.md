# Install and recover the webOS 5 preview

## Before installing

This preview targets Chromium 68 on webOS 5. Its UI baseline was physically tested
on an LG 86UN8570AUD, webOS 5.6.2-21 / firmware 04.64.00. The public 0.3.14 package
uses generic artwork/audio and has build, package and browser verification; it is
not a claim of physical testing on every model.

Full TV controls and native-icon discovery require an already rooted TV with
Homebrew Channel. This package does not root a TV or install Homebrew Channel.
Live app discovery, weather and navigation sounds start Off on a fresh install.
Enable the features you want in Settings → Options.

## Download and install

1. Get `local.lumen.trial_0.3.14_all.ipk` and `SHA256SUMS.txt` from
   [the preview release](https://github.com/xcv58/lumen-webos/releases/tag/webos5-v0.3.14).
2. Verify the download with `shasum -a 256 -c SHA256SUMS.txt` on macOS, or
   `sha256sum -c SHA256SUMS.txt` on Linux, in the download directory.
3. In [Dev Manager Desktop](https://github.com/webosbrew/dev-manager-desktop), use
   your configured TV connection and install the IPK from Apps. Alternatively:

   ```sh
   ares-install --device YOUR_DEVICE local.lumen.trial_0.3.14_all.ipk
   ```

4. Open **Lumen webOS 5** from the TV's app list. Down expands the app grid;
   Back collapses it. Inputs and Control Center are at the top right.
5. Enable “Live app list via Homebrew Channel” in Settings → Options for the live
   app list and native icons. Privileged controls use the existing Homebrew service
   when invoked. Optional weather uses network services;
   optional online photo collections download images to the TV.

The release includes `BUILD-INFO.json` describing the source revision, package
contents and hashes. It contains no private device preferences or connection data.

## Existing trial users

The app ID remains `local.lumen.trial`, so installing over a prior Trial updates
that app rather than creating another copy. Existing preferences load as before;
the fresh-install Off defaults do not rewrite saved choices. Back up important
preferences and any local artwork or audio override before updating.

Public packages replace package-local artwork and sounds with generic assets.
Installing upstream `com.ammar027.lumen` is a separate app and does not migrate
trial preferences. The public preview does not claim automatic compatibility with
upstream 1.1's settings or additional screensavers.

## Home and startup

Installation alone leaves the physical Home key and startup behavior as they are.
This preview does not install a Home remapper or persistent startup/wake helper.
Control Center → LG Home opens the original launcher.

If you separately configured a remapper or startup script, keep its recovery
instructions and disable that configuration before uninstalling its target app.
Such hooks need their own approval and model-specific verification; they are not
required to open this preview from the app list.

## Recovery

- Press the TV's Home key to open LG Home when no separate mapping is installed.
  While the preview responds, Control Center → LG Home provides another route.
- Turn Navigation sounds Off if you do not want focus feedback. Turn “Live app list via Homebrew Channel”
  Off to return to the catalogue provider.
- Remove only **Lumen webOS 5** / `local.lumen.trial` through the TV's app list or
  Dev Manager. The original Lumen app and LG Home remain installed. Uninstalling
  may erase the trial's app-private preferences and cache.
- If a separately installed Home/startup hook targets the preview, restore that
  hook's previous mapping and disable its startup action before removing the app.

Report problems with the model, webOS version, firmware, app version and steps to
reproduce. Remove network addresses, accounts, location and personal content from
logs and screenshots before sharing them.
