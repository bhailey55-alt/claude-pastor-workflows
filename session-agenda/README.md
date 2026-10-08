# Session Agenda Cycle

The monthly elder-board packet, on autopilot. Your treasurer's financials and your clerk's minutes file themselves into the next meeting's folder. Claude drafts the agenda from last month's plus your notes, emails you to review, and sends your admin the print list.

## The weekly rhythm (example: first-Tuesday meetings)

| When | What happens | Who does it |
|---|---|---|
| Any time | Treasurer emails financials; clerk emails minutes | They do, same as now |
| Any time | You record "Session, …" voice notes or drop notes in the folder | You |
| Wed 9 p.m. & Fri 6 a.m. | Attachments and voice-note transcripts get filed into the **upcoming** meeting folder | Google Apps Script (your account, Google's servers) |
| **Thu 7 a.m.** before the meeting | Agenda `.docx` drafted (new and changed lines highlighted). Email to you: *"What do you want [admin] to print tomorrow?"* | Claude scheduled task |
| You, Thursday | Reply "1, 2, 4" or "all" | You |
| **Fri 7 a.m.** | Admin gets the print list with links, copy count, and "hand out Sunday" | Claude scheduled task |
| Sunday | Packets handed out | Your admin |

Thursdays that fall on holidays (Thanksgiving, Christmas Eve, New Year's Eve) move back a week automatically.

## Folder convention

```
Session Minutes/
  2027/
    05January2027/        <- stated meetings: DDMonthYYYY, always on the meeting weekday
    02February2027/
    21Oct2026 Called Meeting/   <- anything else (called meetings) is ignored by the filer
```

The filer picks "upcoming" by date. Minutes sent the morning of a meeting (after it ends) roll to the next one, so the clerk's Oct 6 minutes land in the November folder, ready for approval.

## Files

| File | What it is |
|---|---|
| `SessionFiler.gs` | Google Apps Script. Fill in the CONFIG block, paste into script.google.com, run `installTrigger` once |
| `agenda-draft.prompt.md` | Template for the Thursday scheduled task |
| `print-list.prompt.md` | Template for the Friday scheduled task |
| `agenda_docx.py` | Tiny .docx writer (13 pt, highlights, indents). Kept small so Claude can upload it through the Drive connector |

## Why an Apps Script instead of Claude for the attachments?
Claude's Gmail connector can see attachments but can't hand a multi-megabyte Word file to Drive reliably. The Apps Script copies it inside Google: free, no size limit, and it catches emails that arrive after Thursday.

## Apps Script setup (your Claude walks you through this)
1. **script.google.com** → **New project** → rename it **Session Filer**.
2. Replace `Code.gs` with `SessionFiler.gs` (CONFIG filled in) → **Cmd+S**.
3. **Project Settings** (gear) → **Time zone** = yours.
4. Back in the editor, choose **installTrigger** → **Run**. Approve permissions: on "Google hasn't verified this app" click **Advanced → Go to Session Filer (unsafe)**. That warning is normal for a script you own.
5. The execution log should show anything it filed.
