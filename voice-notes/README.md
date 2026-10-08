# Voice Notes → the right Drive folder

Hold your iPhone's Action Button, talk, tap to stop. A minute later the transcript is a `.txt` file in the right Google Drive folder, sorted by the first words you said.

```
iPhone Action Button ─► Shortcut records audio ─► iCloud Drive/Voice Inbox
                                                        │
                         your Mac (Whisper, fully local) ◄┘
                                                        │
                   reads the opening words: "Session, …" / "Sermon, Advent, …"
                                                        │
                         Google Drive for desktop ─► the matching folder
```

## How to talk to it

**Say the topic, pause, then talk.** Whisper writes your pause as a comma, and that's how the router tells the topic from the content.

| You say | Transcript goes to |
|---|---|
| "Session, add the fellows program for spring." | Session notes folder |
| "Sermon, Advent, idea for the candle lighting…" | Sermons → Advent *(created if new)* |
| "Sermon. Great illustration today about…" | Sermon notes folder |
| "Men's ministry, retreat, spring dates…" | Men's Ministry → Retreat *(created if new)* |
| "Presbytery, follow up with the clerk…" *(new topic)* | Voice Notes → Presbytery *(created and remembered)* |
| "Uh, so I was thinking…" | Voice Notes - Unsorted (nothing is lost) |

It's forgiving: "Adventist" finds your Advent folder, and "Presbytery test" drops the "test." Numbers must match exactly, so "Hebrews 11" never files into "Hebrews 12."

## Files

| File | What it is |
|---|---|
| `install.sh` | One-command installer: Homebrew, whisper.cpp, ffmpeg, the model, and the background service |
| `router.py` | The router. Installed to `~/VoiceRouter/` |
| `routes.example.txt` | Your topic → folder rules. Becomes `~/VoiceRouter/routes.txt`; edit anytime |
| `vocabulary.example.txt` | Names and terms Whisper should spell right. Becomes `~/VoiceRouter/vocabulary.txt` |

## One computer or two

- **Your everyday Mac (default).** It works fine. It only transcribes while the Mac is awake, and when it wakes it catches up on everything you recorded.
- **An always-on Mac (optional).** A Mac mini or old desktop transcribes within a minute, day or night. Same install; just run it on that machine instead.

Apple Silicon (M1 or newer) uses Whisper's large-v3-turbo model: a few seconds per memo, near-best accuracy. Intel Macs get `small.en`, which is slower and a bit less accurate but fine for notes.

## The iPhone Shortcut

1. **Shortcuts** app → **+** → name it **Voice Note**.
2. Add **Record Audio**: *Start Recording* **Immediately**, *Finish Recording* **On Tap**.
3. Add **Save File**: *Ask Where to Save* **off**. Tap the folder and back out to the **top level of iCloud Drive** (where Desktop, Documents, and Shortcuts are listed), then choose **Voice Inbox**. The installer creates that folder; give iCloud a minute to show it on the phone.
4. Run it once from the editor. When iOS asks *"Allow Voice Note to save a file?"*, tap **Always Allow**. Until you do, it fails silently.
5. **Settings → Action Button → Shortcut → Voice Note.**

That's it. iOS already names each recording with the date and time, so no rename step is needed.

## Commands you'll want

```bash
tail -5 ~/VoiceRouter/router.log                 # what happened recently
open -e ~/VoiceRouter/routes.txt                 # edit your topics
open -e ~/VoiceRouter/vocabulary.txt             # edit names Whisper should know
launchctl kickstart -k gui/$(id -u)/org.claudepastor.voicerouter   # run it now
```

Problems? See [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md).
