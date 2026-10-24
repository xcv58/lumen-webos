#!/bin/sh
# Private, separately installed Home adoption helper. Never replace an input or
# app on wake. Home is handled independently by the existing LG Input Hook.
PATH=/bin:/sbin:/usr/bin:/usr/sbin
APP=local.lumen.upstreamtrial
BASE=/var/lib/lumen-trial-launcher
APPDIR=/media/developer/apps/usr/palm/applications/$APP
LOCK=/tmp/lumen-trial-launcher.lock
SETTLE=8
WINDOW=40
MAX_ATTEMPTS=3
[ -d "$APPDIR" ] && [ ! -f "$BASE/disabled" ] || exit 0
if ! mkdir "$LOCK" 2>/dev/null; then
  old=$(cat "$LOCK/pid" 2>/dev/null)
  case "$old" in ''|*[!0-9]*) exit 1 ;; esac
  kill -0 "$old" 2>/dev/null && exit 0
  rm -f "$LOCK/pid"
  rmdir "$LOCK" 2>/dev/null && mkdir "$LOCK" || exit 1
fi
echo $$ > "$LOCK/pid"
trap 'rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null' EXIT
trap 'exit 0' INT TERM

ok() { printf '%s' "$1" | grep -Eq '"returnValue"[[:space:]]*:[[:space:]]*true'; }
field() { printf '%s' "$1" | sed -n 's/.*"'"$2"'"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p'; }
home() {
  case "$1" in
    com.webos.app.home|com.webos.app.fullhome|local.lumen.trial) return 0 ;;
    *) return 1 ;;
  esac
}
normal_wake() {
  # Values observed on this firmware or present in its tvpowerd. Fail closed for
  # CEC, timers, unknown reasons and API failures, even if LG Home appears first.
  case "$1" in remoteKey|localKey|wakeOnWiFi) return 0 ;; *) return 1 ;; esac
}
front() {
  response=$(luna-send -w 3000 -n 1 luna://com.webos.applicationManager/getForegroundAppInfo '{}' 2>/dev/null)
  ok "$response" && field "$response" appId
}
reason() {
  response=$(luna-send -w 3000 -n 1 luna://com.webos.service.tvpower/power/getPowerOnReason '{}' 2>/dev/null)
  ok "$response" && field "$response" reason
}
last=0
active=0
pending=0
previous=""
began=0
stable=0
attempts=0
while [ -d "$APPDIR" ] && [ ! -f "$BASE/disabled" ]; do
  read uptime remainder < /proc/uptime
  now=${uptime%%.*}
  power=$(luna-send -w 3000 -n 1 luna://com.webos.service.tvpower/power/getPowerState '{}' 2>/dev/null)
  state=""
  ok "$power" && state=$(field "$power" state)
  if [ "$state" = Active ]; then
    if [ "$active" -eq 0 ] || { [ "$last" -gt 0 ] && [ $((now-last)) -ge 15 ] && [ "$previous" = Active ]; }; then
      pending=1; began=$now; stable=0; attempts=0
    fi
    active=1
    if [ "$pending" -eq 1 ]; then
      app=$(front)
      if [ "$app" = "$APP" ]; then
        pending=0
        echo "uptime=$now launcher already active; no wake launch"
      elif [ $((now-began)) -ge "$WINDOW" ]; then
        pending=0
        echo "uptime=$now wake window expired; leaving current source"
      elif [ -z "$app" ]; then
        # Readiness errors are not permission to launch over an unknown source.
        stable=0
      elif ! home "$app"; then
        pending=0
        echo "uptime=$now preserved foreground=$app for this wake"
      else
        why=$(reason)
        if ! normal_wake "$why"; then
          pending=0
          echo "uptime=$now preserved wake reason=${why:-unknown}"
        else
          [ "$stable" -eq 0 ] && stable=$now
          if [ $((now-stable)) -ge "$SETTLE" ]; then
            # Recheck after the grace period and immediately before launch. An
            # HDMI switch or app launch cancels the whole wake, not just a retry.
            check_power=$(luna-send -w 3000 -n 1 luna://com.webos.service.tvpower/power/getPowerState '{}' 2>/dev/null)
            check_state=""
            ok "$check_power" && check_state=$(field "$check_power" state)
            check_reason=$(reason)
            check_app=$(front)
            if [ "$check_state" != Active ] || ! normal_wake "$check_reason" || ! home "$check_app"; then
              pending=0
              echo "uptime=$now cancelled wake launch after final source check"
            else
              attempts=$((attempts+1))
              result=$(luna-send -w 3000 -n 1 luna://com.webos.applicationManager/launch "{\"id\":\"$APP\"}" 2>/dev/null)
              if ok "$result"; then
                pending=0
                echo "uptime=$now opened $APP from Home after safe wake"
              elif [ "$attempts" -ge "$MAX_ATTEMPTS" ]; then
                pending=0
                echo "uptime=$now launch unavailable; leaving current source"
              fi
            fi
          fi
        fi
      fi
    fi
  elif [ "$state" = "Screen Saver" ] || [ "$state" = "Screen Off" ]; then
    # Intentional display modes never arm or resume a pending launch.
    pending=0
  else
    case "$state" in Suspend|Standby|"Active Standby"|"Power Off") active=0; pending=0 ;; esac
  fi
  [ -n "$state" ] && previous=$state
  last=$now
  sleep 2
done
