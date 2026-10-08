# Claude Pastor Workflows

Practical automations for pastors who use Claude. You don't have to install these yourself: **your Claude reads the setup instructions and walks you through, one step at a time.**

## What's here

### 🎙️ [Voice notes](voice-notes/README.md)
Hold your iPhone's Action Button and say *"Sermon, Advent, idea for the candle lighting…"*. A minute later the transcript is in your Sermons → Advent folder in Google Drive. *"Session, …"* goes to your elder-meeting folder, and *"Men's ministry, …"* to Men's Ministry. Say a brand-new topic and it makes a folder for it. Transcription runs on your own Mac (Whisper), so your audio never leaves it.

### 📋 [Session agenda cycle](session-agenda/README.md)
- The treasurer's financials and the clerk's minutes file themselves into next month's meeting folder.
- The Thursday before the meeting, Claude drafts the agenda (.docx) from last month's agenda plus your notes and voice notes, with new and changed lines highlighted.
- It emails you: *"What do you want [your admin] to print tomorrow?"* You reply "1, 2, 4," and Friday morning your admin gets the print list.

Use either module, or both. They connect: "Session, …" voice notes flow straight into the agenda.

## What you need

- A **Mac** with the **Claude desktop app (Cowork)**. Apple Silicon (M1 or newer) is best.
- A **Google account** (Gmail, Drive, Calendar), with those connectors turned on in Claude, plus **Google Drive for desktop** on the Mac.
- An **iPhone** with iCloud Drive on (the Action Button is on 15 Pro and newer; older phones can use Back Tap).
- About an hour for setup, and willingness to paste a few commands into Terminal.

## How to install

1. Click the green **Code** button → **Download ZIP**, and unzip it (Downloads is fine).
2. Open the **Claude desktop app → Cowork**, choose **Work in a folder**, and pick the unzipped folder.
3. Say: **"Read SETUP_FOR_CLAUDE.md and set this up for me."**

Your Claude confirms the assumptions, asks you questions (your folders, your treasurer's and clerk's emails, when you meet), builds what it can itself, and hands you one step at a time for the parts that need your hands.

## One computer or two?
Most people run everything on the Mac they already work on. It transcribes whenever the Mac is awake and catches up when it wakes. An always-on Mac (an old Mac mini, say) gets your transcripts within a minute, day or night. Both work; setup asks which you have.

## Privacy
- **The code contains no personal data.** Your settings live only on your Mac and in your Google account.
- **Your audio stays on your Mac.** Whisper runs locally.
- **Your documents stay in your Google Drive.** The Apps Script runs under your Google account.
- Claude reads your Drive and Gmail only through the connectors you've enabled.

## Updating
Download the newest ZIP and say to your Claude: "Update my voice router from this folder." Re-running `voice-notes/install.sh` updates the router and keeps your topics and vocabulary.

## Problems?
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md). Each problem listed there came up during the first real install.

---
Built by Pastor Ben Hailey with Claude. Free to use and adapt ([MIT](LICENSE)). Improvements welcome: open an issue or pull request.
