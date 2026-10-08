#!/bin/bash
# Voice Router installer (claude-pastor-workflows / voice-notes)
# iPhone recordings in iCloud Drive/Voice Inbox -> Whisper (on this Mac) -> Google Drive folder by topic.
#
# Run from this folder:   bash install.sh
# Safe to re-run: updates the router, keeps your routes.txt and vocabulary.txt edits.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/VoiceRouter"
INBOX="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Voice Inbox"
PLIST="$HOME/Library/LaunchAgents/org.claudepastor.voicerouter.plist"
echo "==> Voice Router install"
mkdir -p "$BASE/models" "$INBOX/Processed" "$HOME/Library/LaunchAgents"

# 1. Homebrew (package manager)
if [ "$(uname -m)" = "arm64" ]; then BREW=/opt/homebrew/bin/brew; else BREW=/usr/local/bin/brew; fi
if [ ! -x "$BREW" ]; then
  echo "==> Installing Homebrew (it will ask for your Mac password)"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
eval "$("$BREW" shellenv)"

# 2. Whisper (whisper.cpp) + ffmpeg (audio conversion)
echo "==> Installing whisper.cpp and ffmpeg"
brew install whisper-cpp ffmpeg

# 3. Whisper model: best quality on Apple Silicon, lighter model on Intel
if [ "$(uname -m)" = "arm64" ]; then MODEL_NAME=ggml-large-v3-turbo.bin; SIZE="~1.6 GB"
else MODEL_NAME=ggml-small.en.bin; SIZE="~470 MB"; fi
MODEL="$BASE/models/$MODEL_NAME"
if [ ! -s "$MODEL" ]; then
  echo "==> Downloading Whisper model $MODEL_NAME ($SIZE, one-time)"
  curl -L --fail -o "$MODEL.part" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$MODEL_NAME"
  mv "$MODEL.part" "$MODEL"
fi

# 4. Router script + your settings (settings are never overwritten)
cp "$HERE/router.py" "$BASE/router.py"
[ -f "$BASE/routes.txt" ]     || cp "$HERE/routes.example.txt"     "$BASE/routes.txt"
[ -f "$BASE/vocabulary.txt" ] || cp "$HERE/vocabulary.example.txt" "$BASE/vocabulary.txt"

cat > "$BASE/run.sh" <<'SHEOF'
#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
exec /usr/bin/python3 "$HOME/VoiceRouter/router.py"
SHEOF
chmod +x "$BASE/run.sh"

# 5. Background service: runs whenever Voice Inbox changes, plus every 5 min as backup.
#    On a laptop it simply catches up when the Mac wakes.
cat > "$PLIST" <<PLEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>org.claudepastor.voicerouter</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$BASE/run.sh</string></array>
  <key>WatchPaths</key><array><string>$INBOX</string></array>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$BASE/launchd.log</string>
  <key>StandardErrorPath</key><string>$BASE/launchd.log</string>
</dict>
</plist>
PLEOF
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

# 6. Self-check
WHISPER="$(command -v whisper-cli || command -v whisper-cpp || true)"
echo ""
echo "==> Check:"
[ -n "$WHISPER" ] && echo "  OK  whisper: $WHISPER" || echo "  !!  whisper binary not found"
[ -s "$MODEL" ]   && echo "  OK  model: $MODEL_NAME" || echo "  !!  model missing"
ls -d "$HOME"/Library/CloudStorage/GoogleDrive-* >/dev/null 2>&1 \
  && echo "  OK  Google Drive for desktop found" || echo "  !!  Google Drive for desktop not found (install and sign in)"
launchctl print "gui/$(id -u)/org.claudepastor.voicerouter" >/dev/null 2>&1 \
  && echo "  OK  background service running" || echo "  !!  service not loaded"
echo ""
echo "NEXT: System Settings > Privacy & Security > Full Disk Access > + > Cmd+Shift+G > /bin/bash > Open (toggle on)."
echo "Inbox: iCloud Drive/Voice Inbox   Rules: ~/VoiceRouter/routes.txt   Log: ~/VoiceRouter/router.log"
