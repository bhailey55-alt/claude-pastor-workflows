# Troubleshooting

Each of these happened during the first real install.

## Voice notes

**The Shortcut "runs" but no recording appears anywhere.**
iOS hasn't been given permission to save. Run the Shortcut from inside the Shortcuts editor (▶). When you see *"Allow … to save a file?"*, tap **Always Allow**. It doesn't ask when launched from the Action Button, it just fails, so do this once from the editor.

**Shortcut's Save File points to the wrong "Voice Inbox."**
The folder picker can land in *iCloud Drive → Shortcuts*. Tap the folder in the Save File action, back out to the top level of iCloud Drive (the screen showing Desktop, Documents, Shortcuts), and pick **Voice Inbox** there.

**`PermissionError: Operation not permitted` in `~/VoiceRouter/launchd.log`.**
Background runs need Full Disk Access for bash: **System Settings → Privacy & Security → Full Disk Access → + → Cmd+Shift+G → `/bin/bash`**. One error from the moment of install, before you granted it, is normal.

**`Resource deadlock avoided` (on reading the audio, or on writing to Google Drive).**
macOS blocks background processes from downloading iCloud or Google Drive "placeholder" files. `router.py` opts itself back in (`setiopolicy_np`) and asks iCloud to download first (`brctl download`). If you still see it, make sure you're on the latest `router.py`, then run `launchctl kickstart -k gui/$(id -u)/org.claudepastor.voicerouter`.

**The installer says "No such file or directory" when run from Google Drive.**
Drive for desktop hadn't synced the file yet. Click the Drive icon in the menu bar, wait for "up to date," and run it again.

**A note went to the wrong place.**
Look at what Whisper actually heard: `tail ~/VoiceRouter/router.log` shows the destination, and the `.txt` shows the words. Usually there was no pause after the topic ("Sermon Advent test" instead of "Sermon, Advent, …"). The router tolerates that for up to two words after the topic, but a clear pause is most reliable. Add Whisper's odd spellings as extra keywords in `routes.txt`, and add names to `vocabulary.txt`.

**A junk folder got created ("Presbytery Test").**
Delete the folder in Drive and delete its auto-added line at the bottom of `~/VoiceRouter/routes.txt`.

**Nothing happens on a laptop.**
It only runs while the Mac is awake. Open the lid, give it a minute, and it catches up.

## Session agenda

**The Apps Script says "Google hasn't verified this app."**
That's normal for a script you wrote yourself. Click **Advanced → Go to Session Filer (unsafe) → Allow**.

**Financials landed in the wrong month's folder.**
"Upcoming" is computed from the date the email arrived. A treasurer who sends late can land a month later. Drag the file over; the agenda task reads whatever is in the folder on draft day.

**Called-meeting folder got the financials.**
Only folders named `DDMonthYYYY` on the stated-meeting weekday count. Name called meetings differently (e.g. `21Oct2026 Called Meeting`).

**No Thursday email.**
The task runs only while the Claude app is open. It also does nothing on non-draft weeks, which is by design. Check the Scheduled sidebar for the last run.

**The agenda .docx didn't upload, or opened blank in Drive's preview.**
Drive's preview sometimes shows the small generated .docx as blank; open it in Word. If the email said the upload failed twice, ask Claude to rebuild it.
