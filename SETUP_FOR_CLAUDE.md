# SETUP_FOR_CLAUDE.md

**Claude: this file is your instructions.** A pastor has downloaded this repo and asked you to set it up. Follow these rules for the whole install:

- **One step at a time.** Give one instruction, wait for the result, then give the next. Pastors are busy and capable but are not developers. Don't dump the whole plan on them.
- **One question at a time.** Use your multiple-choice question tool when you have one.
- **Do what you can yourself.** Create Drive folders, write config files, and create scheduled tasks with your own tools. Only hand the pastor steps that need their hands: Terminal on their Mac, their iPhone, script.google.com, and macOS permission dialogs.
- **Never guess an email address, folder, or name.** Ask, or look it up with the connectors and confirm.
- **Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) before you start.** Every problem in it really happened during the first install.

---

## Step 0: Confirm the assumptions (ask before anything else)

Read these back to the pastor and confirm each one. If any is false, say what changes, or stop.

1. **Claude desktop app with Cowork, on a Mac.** The scheduled tasks need it. The voice notes module needs a Mac too (Apple Silicon M1 or newer recommended; Intel works with a lighter model).
2. **Google account (Gmail, Drive, Calendar)**, with the **Gmail, Google Drive, and Google Calendar connectors enabled in Claude**. Check that your tools can reach them.
3. **Google Drive for desktop** installed on the Mac and signed in. In Finder there should be a Google Drive item with *My Drive*, and *Shared drives* if they use any.
4. **iCloud Drive on** for both the iPhone and the Mac, with the same Apple ID.
5. **An iPhone with an Action Button** (15 Pro or newer). Without one, use Back Tap (Settings → Accessibility → Touch → Back Tap) or a Home Screen icon.
6. **Willing to paste a few commands into Terminal.** You'll give the exact text every time.
7. **Their own data stays theirs.** Everything runs on their Mac, their Google account, and their Claude. Whisper transcribes locally; no audio leaves the Mac.

## Step 1: Pick modules

Ask which they want:

- **Voice notes**: Action Button → transcript filed in Drive by topic. ([voice-notes/](voice-notes/README.md))
- **Session agenda cycle**: financials and minutes auto-filed, Thursday agenda draft, print list to the admin. ([session-agenda/](session-agenda/README.md))
- **Both** (recommended). The modules connect: "Session, …" voice notes flow into the agenda.

Also ask **one computer or two**. The default is their everyday Mac, which transcribes whenever it's awake. If they have an always-on Mac (a Mac mini, say), the voice-notes install goes there instead; the Cowork scheduled tasks still run on whichever Mac has the Claude app open.

## Step 2: Get the files onto the Mac

Have them download the repo (green **Code** button → **Download ZIP**) and unzip it, e.g. into Downloads. Then request access to that folder with your directory tool, so you can read the files and they can run `install.sh` from it.

---

## Module A: Voice notes

### A1. Interview (one question at a time)
1. **Topics.** What do they want to say at the start of a note? Offer the defaults: Session, Sermon, Men's ministry, Women's ministry, Youth.
2. **Where each topic goes.** Search their Drive with the connector and propose real folders. For ministries, use or create a `Voice Notes` subfolder so transcripts don't mix with documents. For Sermon, ask whether "Sermon, Advent" should create subfolders under their Sermons folder (the `sub:` setting).
3. **The Session folder.** If they're doing Module B, the Session topic must point to a `_Voice Inbox` folder inside their Session Minutes folder. Create it, and keep its Drive ID for the Apps Script CONFIG.
4. **Vocabulary.** Church name, staff and elder names, denomination terms (PCA, BCO…), current sermon series. Whisper uses these to spell names right.

Create any missing folders with the Drive connector. Create `My Drive/Voice Notes` and `My Drive/Voice Notes - Unsorted` too.

### A2. Install (the pastor runs it; on the always-on Mac if they chose two computers)
Give them one command (adjust the path to where they unzipped):
```bash
cd ~/Downloads/claude-pastor-workflows-main/voice-notes && bash install.sh
```
Homebrew may ask for their Mac password. The model download takes a few minutes. The **Check:** section at the end should show four OK lines; work through any `!!` line before moving on.

### A3. Full Disk Access (required)
**System Settings → Privacy & Security → Full Disk Access → + → Cmd+Shift+G → `/bin/bash` → Open**, with the toggle on. Leave the other entries alone. Without this, background runs fail silently.

### A4. Write their rules
Request access to `~/VoiceRouter` with your directory tool, then write `routes.txt` from the interview, following the format in `routes.example.txt` (paths are relative to the Google Drive root as Finder shows it, `*` = any shared drive name), and `vocabulary.txt`. Keep the `NEWTOPIC` and `UNSORTED` lines. Changes take effect on the next recording.

### A5. The iPhone Shortcut
Walk them through it one step at a time, using the steps in [voice-notes/README.md](voice-notes/README.md#the-iphone-shortcut). The two things people miss:
- **Save File** has to point at the **top-level** iCloud Drive → Voice Inbox, not a Voice Inbox inside the Shortcuts folder.
- On the first run, tap **Always Allow** at "Allow … to save a file?". Until then it fails silently.

### A6. Test
Have them record three notes: "Session, this is a test", "Sermon, Advent, test", and something with no topic. After a minute, check the log:
```bash
tail -5 ~/VoiceRouter/router.log
```
Confirm each landed in the right folder using the Drive connector, then **delete the test transcripts** so they don't end up in a real agenda. If the topic was a brand-new word, also delete its auto-added line at the bottom of `routes.txt`.

---

## Module B: Session agenda cycle

### B1. Interview (one question at a time)
1. Board name ("Session", "Elders", "Board") and **stated-meeting rule** (e.g. "first Tuesday at 6:30 a.m.") and location.
2. Timezone.
3. Where meeting folders live. Find their minutes folder in Drive, or propose `Session Minutes/<year>/DDMonthYYYY`. Read last year's folders to learn their pattern.
4. **Treasurer**: email address and how the financials email subject usually reads (search their Gmail to confirm, then build the Gmail query, e.g. `subject:(monthly financials) has:attachment`).
5. **Clerk**: same for minutes (e.g. `subject:minutes has:attachment`).
6. Membership updates: who puts them where?
7. **Admin** who prints: name and email, copies, when packets are handed out (e.g. "Sunday before the meeting at church"), and how the pastor signs short emails.
8. **Draft day and time** (default: Thursday 7 a.m., 5 days before a Tuesday meeting) and print day (the next morning).
9. Their agenda's sections: read last month's agenda and confirm.

### B2. Build the folders
With the Drive connector, create this year's and next year's meeting folders (`DDMonthYYYY`, computed from the meeting rule; double-check the dates in bash), plus `_Voice Inbox` if they're using Module A.

### B3. Google Apps Script
Fill in the CONFIG block of `session-agenda/SessionFiler.gs`:
- `SESSION_MINUTES_ID`: the Drive ID of the folder that holds the year folders
- `VOICE_INBOX_ID`: the `_Voice Inbox` folder ID, or `''`
- `START_AFTER`: about a week ago, so old mail isn't backfilled
- `MEETING_WEEKDAY`, `MEETING_OVER_HOUR`, `SEARCHES`, `RUN_DAYS`: the night before the draft and the morning of print day

Save the filled-in copy where they can open it, then walk them through **script.google.com** one step at a time (see [session-agenda/README.md](session-agenda/README.md#apps-script-setup-your-claude-walks-you-through-this)). Have them paste the execution log back to you, and confirm in Drive anything it filed.

### B4. Scheduled tasks
Fill in `agenda-draft.prompt.md` and `print-list.prompt.md`. Replace every `{{PLACEHOLDER}}`, paste the contents of `agenda_docx.py` in place of `{{AGENDA_DOCX_PY}}`, and delete the note block at the top. Each prompt must stand on its own: a future Claude reads it cold. Then create two scheduled tasks with your scheduled-task tool:
- `session-agenda-draft`: draft day and time (e.g. `0 7 * * 4`)
- `session-print-list`: the next day, morning and noon (e.g. `0 7,12 * * 5`)

Tell the pastor:
- **Tasks only run while the Claude desktop app is open.** If the Mac is closed, a task runs the next time the app opens.
- **Tasks may be saved in auto-approve mode**, which sends email without asking. They can switch a task to "Manually approve" in the Scheduled sidebar.
- **Tell the admin it's coming.** An email from the pastor's account arriving each month shouldn't surprise anyone.

### B5. First run
Tell them the date of the first live draft. Offer to check on that run afterward: did the .docx upload verify, and does the email read right?

---

## Step 3: Hand-off
Give a short summary: what runs when, where the files live, and how to change things:
- **New voice topic:** just say it ("Presbytery, …"). Its folder is created automatically.
- **Change a topic's folder:** edit `~/VoiceRouter/routes.txt`, or ask Claude.
- **A meeting moved:** rename its folder to the new date, and everything follows.
- **Something's off:** `tail ~/VoiceRouter/router.log`, the Apps Script execution log, and [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
