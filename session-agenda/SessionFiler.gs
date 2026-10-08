/**
 * Session Folder Filer — Google Apps Script  (claude-pastor-workflows / session-agenda)
 *
 * Runs twice a week under YOUR Google account (free, on Google's servers).
 * Files into the UPCOMING stated-meeting folder  (Session Minutes / YYYY / DDMonthYYYY):
 *   1. Email attachments from the senders below (treasurer's financials, clerk's minutes)
 *   2. Voice-note transcripts (.txt) dropped in the Voice Inbox folder (optional)
 *      -> moved into the upcoming meeting folder as "Voice note YYYY-MM-DD HHmm.txt"
 *
 * "Upcoming" = the first meeting-day folder dated after the email/note arrived.
 * A meeting counts as over at MEETING_OVER_HOUR on its day, so minutes sent the
 * same day roll to the next meeting. Folders dated on other weekdays (called
 * meetings) are ignored.
 *
 * SETUP: fill in CONFIG, set Project Settings -> Time zone, then run installTrigger once.
 */

// ======================= CONFIG (your Claude fills this in) =======================
const SESSION_MINUTES_ID = 'PASTE_SESSION_MINUTES_FOLDER_ID';   // Drive folder that holds the year folders
const VOICE_INBOX_ID     = '';          // Drive folder for Session voice notes; '' to skip
const START_AFTER        = '2026/01/01';   // ignore mail older than this (YYYY/MM/DD)
const MEETING_WEEKDAY    = 2;           // 0=Sun 1=Mon 2=Tue 3=Wed 4=Thu 5=Fri 6=Sat
const MEETING_OVER_HOUR  = 10;          // meeting is "over" at this hour on its day
const SEARCHES = [                      // who sends what. Add or remove lines freely.
  { from: 'treasurer@yourchurch.org', query: 'subject:(monthly financials) has:attachment' },
  { from: 'clerk@example.com',        query: 'subject:minutes has:attachment' },
];
const RUN_DAYS = [                      // when to run (day, hour). Default: the night before
  { day: ScriptApp.WeekDay.WEDNESDAY, hour: 21 },   // the Thursday agenda draft, and the
  { day: ScriptApp.WeekDay.FRIDAY,    hour: 6  },   // morning the print list goes out.
];
// ==================================================================================

const MONTHS = ['january','february','march','april','may','june','july',
                'august','september','october','november','december'];

function run() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return;           // previous run still going
  try {
    const meetings = listMeetings_();
    fileEmail_(meetings);
    fileVoiceNotes_(meetings);
  } finally {
    lock.releaseLock();
  }
}

/** All stated-meeting folders, sorted by date. */
function listMeetings_() {
  const out = [];
  const years = DriveApp.getFolderById(SESSION_MINUTES_ID).getFolders();
  while (years.hasNext()) {
    const y = years.next();
    if (!/^\d{4}$/.test(y.getName())) continue;
    const months = y.getFolders();
    while (months.hasNext()) {
      const f = months.next();
      const m = f.getName().match(/^(\d{1,2})([A-Za-z]+)(\d{4})$/);
      if (!m) continue;
      const mi = MONTHS.indexOf(m[2].toLowerCase());
      if (mi < 0) continue;
      const d = new Date(+m[3], mi, +m[1], MEETING_OVER_HOUR, 0, 0);
      if (d.getDay() !== MEETING_WEEKDAY) continue;      // stated-meeting weekday only
      out.push({ date: d, folder: f });
    }
  }
  return out.sort((a, b) => a.date - b.date);
}

function upcoming_(meetings, when) {
  return meetings.find(m => m.date > when) || null;
}

/** Treasurer's financials + clerk's minutes (SEARCHES) → upcoming folder. */
function fileEmail_(meetings) {
  const props = PropertiesService.getScriptProperties();
  const done = JSON.parse(props.getProperty('doneMsgs') || '[]');

  SEARCHES.forEach(s => {
    const q = `from:${s.from} ${s.query} after:${START_AFTER}`;
    GmailApp.search(q, 0, 50).forEach(thread => {
      thread.getMessages().forEach(msg => {
        const id = msg.getId();
        if (done.includes(id)) return;
        // Only the sender's own messages (skip replies from others in the thread)
        if (msg.getFrom().toLowerCase().indexOf(s.from) === -1) { done.push(id); return; }
        const atts = msg.getAttachments({ includeInlineImages: false });
        if (!atts.length) { done.push(id); return; }

        const mtg = upcoming_(meetings, msg.getDate());
        if (!mtg) {                                   // no folder yet — retry next run
          console.log('No upcoming folder for: ' + msg.getSubject());
          return;
        }
        atts.forEach(a => {
          let name = a.getName();
          if (mtg.folder.getFilesByName(name).hasNext()) {   // a revision with same filename
            const stamp = Utilities.formatDate(msg.getDate(), Session.getScriptTimeZone(), 'MMM d');
            name = name.replace(/(\.[^.]+)?$/, ` (rev ${stamp})$1`);
          }
          mtg.folder.createFile(a.copyBlob()).setName(name);
        });
        console.log(`Filed ${atts.length} file(s) from "${msg.getSubject()}" → ${mtg.folder.getName()}`);
        done.push(id);
      });
    });
  });

  props.setProperty('doneMsgs', JSON.stringify(done.slice(-500)));
}

/** Voice transcripts (.txt from your Mac) → moved into the upcoming meeting folder. */
function fileVoiceNotes_(meetings) {
  if (!VOICE_INBOX_ID) return;
  const inbox = DriveApp.getFolderById(VOICE_INBOX_ID);
  const it = inbox.getFiles();
  while (it.hasNext()) {
    const f = it.next();
    if (!/\.(txt|md)$/i.test(f.getName())) continue;   // transcripts only
    const when = f.getDateCreated();
    const mtg = upcoming_(meetings, when);
    if (!mtg) continue;
    const stamp = Utilities.formatDate(when, Session.getScriptTimeZone(), 'yyyy-MM-dd HHmm');
    f.setName('Voice note ' + stamp + '.txt');
    f.moveTo(mtg.folder);
    console.log(`Voice note ${stamp} → ${mtg.folder.getName()}`);
  }
}

/**
 * Run once. Replaces any existing triggers with the RUN_DAYS schedule, then runs now.
 */
function installTrigger() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  RUN_DAYS.forEach(r => ScriptApp.newTrigger('run').timeBased().onWeekDay(r.day).atHour(r.hour).create());
  run();
}
