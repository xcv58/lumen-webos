# Optional TV Home adoption

This helper is separately installed private TV configuration. It is not bundled
with the app and no build script installs it. Root access and explicit owner
authorization are required to change persistent Home/startup behavior.

The existing LG Input Hook maps only Home (773) to
`local.lumen.upstreamtrial`. Other mappings remain unchanged. The app and its
manifest stay unchanged; this does not set a firmware-specific native default
Home category. Both the previous accepted launcher and LG Home remain installed.

The existing Homebrew init script starts `on-power.sh` from
`/var/lib/lumen-trial-launcher/on-power.sh`. The legacy directory name is retained
so existing disable/recovery procedures still apply. A PID lock prevents duplicate
watchers. The helper exits if its target is removed or the existing `disabled`
marker is present.

The previous helper launched unconditionally whenever power became Active. That
could cover a console's HDMI video just after HDMI-CEC woke the TV. The replacement
uses these rules:

- Observe only a bounded startup/wake period; do not redirect ordinary app use.
- Leave HDMI, AV, Live TV and any other non-launcher foreground app alone for the
  entire wake, even if LG Home later reappears.
- Only consider LG Home or the previous accepted launcher, after eight seconds
  of valid launcher observations. If the new trial is already visible, do nothing.
- Require a known normal power reason (`remoteKey`, `localKey`, or `wakeOnWiFi`).
  These names were read from the target firmware or observed on it. Other reasons,
  including CEC, are not eligible. An unavailable/unknown reason skips launch.
- Check power, reason and foreground again immediately before requesting launch.
  Foreground readiness errors restart the grace period, within a forty-second
  window. At most three failed launch requests are made, rechecking each time.
- Treat Screen Off and Screen Saver as intentional display modes.

Consequently, waking with the LG remote while an HDMI source is restored also
preserves that source. Home always explicitly opens the new trial. No CEC,
Simplink, audio or global input preferences are changed.

Before applying, save the current Home mapping, helper, init script, file modes
and app manifests/hashes locally and in a root-only backup on the TV. Validate
the staged helper with `/bin/sh -n`. Stop only the verified PID whose command
line names the old helper, then replace the helper and Home mapping atomically.
Do not reinject Input Hook or change other remote bindings.

To suspend automatic wake behavior, create
`/var/lib/lumen-trial-launcher/disabled`. The Home mapping remains usable. To
return Home to the earlier app, change only mapping 773 back to
`{"action":"launch","id":"local.lumen.trial"}`. Keep unrelated mappings.
Restoring the old unconditional helper also restores the console-wake defect;
prefer keeping the new guard or leaving automatic wake disabled.

Run `node compat/tests/wake-helper-tests.mjs` for the isolated state fixtures.
Real power-on/CEC and physical Home acceptance are separate device checks. On
2026-10-24, the owner confirmed both on the target LG TV: console wake kept the
game HDMI input stable, and the physical Home button opened the new launcher.
