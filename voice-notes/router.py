#!/usr/bin/env python3
"""
Voice Router — runs on your Mac
Watches iCloud Drive/Voice Inbox for iPhone recordings, transcribes them with
whisper.cpp (local, Metal GPU), reads the first few words for a routing keyword,
and saves the transcript as .txt into the matching Google Drive folder.
Routing rules live in ~/VoiceRouter/routes.txt (edit anytime, no restart needed).
Part of claude-pastor-workflows (MIT). See voice-notes/README.md.
"""
import datetime, difflib, fcntl, glob, os, re, shutil, subprocess, sys, tempfile, time

HOME   = os.path.expanduser("~")
BASE   = os.path.join(HOME, "VoiceRouter")
INBOX  = os.path.join(HOME, "Library/Mobile Documents/com~apple~CloudDocs/Voice Inbox")
DONE   = os.path.join(INBOX, "Processed")
ROUTES = os.path.join(BASE, "routes.txt")
LOG    = os.path.join(BASE, "router.log")
AUDIO  = (".m4a", ".mp3", ".wav", ".aac", ".caf", ".mp4", ".mov", ".qta")
HEAD_WORDS = 8   # only look for the keyword in the first N words
VOCAB  = os.path.join(BASE, "vocabulary.txt")   # optional: names/terms Whisper should spell right
DEFAULT_PROMPT = ("Session, elders, deacons, presbytery, men's ministry, women's ministry, "
                  "youth, sermon.")

def whisper_prompt():
    """A short vocabulary hint (church name, staff names, sermon series) helps Whisper."""
    try:
        with open(VOCAB) as f:
            words = " ".join(l.strip() for l in f if l.strip() and not l.startswith("#"))
        return words[:600] or DEFAULT_PROMPT
    except OSError:
        return DEFAULT_PROMPT

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}  {msg}\n")

def tool(name):
    for d in ("/opt/homebrew/bin", "/usr/local/bin"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return shutil.which(name)

def drive_roots():
    return glob.glob(os.path.join(HOME, "Library/CloudStorage/GoogleDrive-*"))

def load_routes():
    """Lines: 'kw1, kw2 | Folder/Path/inside/Drive [| sub: Parent/For/New/Subtopics]'
    ('*' = any shared drive). Special keys: UNSORTED, NEWTOPIC."""
    routes, special = [], {}
    with open(ROUTES) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            parts = [x.strip() for x in line.split("|")]
            kws, path = parts[0], parts[1]
            sub = None
            for extra in parts[2:]:
                if extra.lower().startswith("sub:"):
                    sub = extra[4:].strip()
            if kws.upper() in ("UNSORTED", "NEWTOPIC"):
                special[kws.upper()] = path
                continue
            label = kws.split(",")[0].strip()
            for kw in kws.split(","):
                kw = kw.strip().lower().replace("’", "'")
                if kw:
                    routes.append((kw, label, path, sub))
    return routes, special

def route(text, routes, max_words=HEAD_WORDS):
    """Earliest keyword in the opening words wins; ties go to the longer phrase.
    Returns (label, path, sub_parent, keyword) or None."""
    words = re.findall(r"[a-z0-9']+", text.lower().replace("’", "'"))[:max_words]
    head = " ".join(words)
    best = None
    for kw, label, path, sub in routes:
        m = re.search(r"(?<![a-z'])" + re.escape(kw) + r"(?![a-z])", head)
        if m:
            key = (m.start(), -len(kw))
            if best is None or key < best[0]:
                best = (key, (label, path, sub, kw))
    return best[1] if best else None

# Words that mean "this isn't a topic name, it's the start of a sentence"
FILLER = {"uh", "um", "okay", "ok", "so", "and", "but", "the", "a", "an", "i", "i'm",
          "we", "we're", "you", "he", "she", "they", "this", "that", "it", "it's",
          "just", "test", "testing", "hey", "alright", "well", "need", "remember",
          "note", "reminder", "thinking", "there", "here", "what", "how", "can"}
# Words dropped from the END of a topic name ("Advent folder", "Presbytery test")
TAIL = {"folder", "notes", "note", "file", "test", "testing", "tests", "one", "two", "three"}

def chunks(text):
    """Split the opening of a transcript at pauses (Whisper's commas/periods)."""
    return [c.strip() for c in re.split(r"[,.;:!?—–]+", text) if c.strip()]

def topic_name(chunk, max_words=3):
    """'advent folder' -> 'Advent'. None if it looks like a sentence, not a name."""
    words = re.findall(r"[A-Za-z0-9'’]+", chunk)
    while words and words[-1].lower() in TAIL:
        words.pop()
    if not 1 <= len(words) <= max_words or words[0].lower() in FILLER:
        return None
    return " ".join(w if w.isupper() else w[:1].upper() + w[1:] for w in words)

def close(a, b):
    """Forgiving match for Whisper spellings ('Adventist' ~ 'Advent').
    Anything with a number must match exactly (Hebrews 11 is not Hebrews 12)."""
    a, b = a.lower(), b.lower()
    if a == b:
        return True
    if re.search(r"\d", a + b) or min(len(a), len(b)) < 5:
        return False
    if a.startswith(b) or b.startswith(a):
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.8

def find_child(parent_rel, name):
    """Existing subfolder of parent matching this name (exact first, then close)."""
    for root in drive_roots():
        for parent in glob.glob(os.path.join(root, parent_rel)):
            try:
                dirs = [e for e in os.listdir(parent)
                        if not e.startswith(".") and os.path.isdir(os.path.join(parent, e))]
            except OSError:
                continue
            for e in dirs:
                if e.lower() == name.lower():
                    return os.path.join(parent_rel, e)
            for e in dirs:
                if close(e, name):
                    return os.path.join(parent_rel, e)
    return None

def add_route(name, rel, sub=None):
    """Remember a new topic so next time 'Presbytery, ...' goes straight there."""
    line = f"{name.lower()} | {rel}" + (f" | sub: {sub}" if sub else "")
    with open(ROUTES, "a") as f:
        f.write(f"\n# added automatically {datetime.date.today()}\n{line}\n")
    log(f"NEW ROUTE  {line}")

def after_keyword(chunk, kw):
    """Words in the same chunk after the keyword: 'Sermon Advent test' -> 'Advent test'."""
    m = re.search(re.escape(kw), chunk.replace("’", "'"), re.I)
    return chunk[m.end():] if m else ""

def pick_destination(text, routes, special):
    """Returns (label, rel_path). Handles known topics, 'Topic, Subtopic', and new topics."""
    cs = chunks(text)
    first = cs[0] if cs else ""
    hit = route(text, routes)
    if hit:
        label, path, sub, kw = hit
        if sub and route(first, routes, max_words=4) == hit:
            # "Sermon, Advent, ..." (pause)  or  "Sermon Advent ..." (no pause, max 2 words)
            name = topic_name(cs[1], max_words=2) if len(cs) > 1 else None
            if not name:
                name = topic_name(after_keyword(first, kw), max_words=2)
            if name:   # existing subfolder (exact or close spelling) or a new one
                rel = find_child(sub, name) or os.path.join(sub, name)
                return os.path.basename(rel), rel
        return label, path
    # No known keyword: brand-new top-level topic from the first chunk
    name = topic_name(first)
    if not name:
        return "unsorted", special.get("UNSORTED")
    for kw, label, path, sub in routes:            # close to an existing topic? use it
        if close(kw, name):
            return label, path
    if special.get("NEWTOPIC"):
        existing = find_child(special["NEWTOPIC"], name)
        if existing:
            return os.path.basename(existing), existing
        rel = os.path.join(special["NEWTOPIC"], name)
        add_route(name, rel, sub=rel)
        return name, rel
    return "unsorted", special.get("UNSORTED")

def resolve(rel):
    """Find the Drive folder for a relative path; create the last folder if missing."""
    if not rel:
        return None
    for root in drive_roots():
        hits = glob.glob(os.path.join(root, rel))
        if hits:
            return hits[0]
        parents = glob.glob(os.path.join(root, os.path.dirname(rel)))
        if parents:
            p = os.path.join(parents[0], os.path.basename(rel))
            os.makedirs(p, exist_ok=True)
            return p
    return None

def model_path():
    """Best installed model: large-v3-turbo on Apple Silicon, small.en on Intel Macs."""
    for m in ("ggml-large-v3-turbo.bin", "ggml-small.en.bin", "ggml-base.en.bin"):
        p = os.path.join(BASE, "models", m)
        if os.path.exists(p):
            return p
    raise FileNotFoundError("no Whisper model in ~/VoiceRouter/models (re-run install.sh)")

def transcribe(src):
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        subprocess.run([tool("ffmpeg"), "-y", "-loglevel", "error", "-i", src,
                        "-ar", "16000", "-ac", "1", wav], check=True)
        out = os.path.join(tmp, "a")
        whisper = tool("whisper-cli") or tool("whisper-cpp")
        subprocess.run([whisper, "-m", model_path(), "-f", wav, "-l", "en", "-nt",
                        "--prompt", whisper_prompt(), "-otxt", "-of", out],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(out + ".txt") as f:
            return " ".join(l.strip() for l in f if l.strip())

SF_DATALESS = 0x40000000   # macOS flag: iCloud placeholder, contents not on disk yet

def is_dataless(path):
    try:
        return bool(os.stat(path).st_flags & SF_DATALESS)
    except (OSError, AttributeError):
        return False

def ensure_local(path, wait=90):
    """Ask iCloud to download the file and wait for it. Background processes
    can't read iCloud placeholders directly ('Resource deadlock avoided')."""
    if not is_dataless(path):
        return True
    subprocess.run(["brctl", "download", path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(wait // 3):
        time.sleep(3)
        if not is_dataless(path):
            return True
    return False

def stable(path):
    """True once iCloud has finished writing the file."""
    try:
        a = os.path.getsize(path); time.sleep(3); b = os.path.getsize(path)
        return a == b and a > 0
    except OSError:
        return False

def allow_cloud_files():
    """Background (launchd) processes are barred from touching cloud files that
    aren't on disk yet — iCloud and Google Drive both return 'Resource deadlock
    avoided'. Opt this process (and ffmpeg/whisper it launches) back in."""
    try:
        import ctypes
        libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
        # IOPOL_TYPE_VFS_MATERIALIZE_DATALESS_FILES=3, IOPOL_SCOPE_PROCESS=0, ON=2
        libc.setiopolicy_np(3, 0, 2)
    except Exception as e:
        log(f"warning: could not set iopolicy: {e}")

def main():
    allow_cloud_files()
    os.makedirs(DONE, exist_ok=True)
    lock = open(os.path.join(BASE, ".lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)   # one run at a time
    except OSError:
        return
    routes, special = load_routes()

    for name in sorted(os.listdir(INBOX)):
        src = os.path.join(INBOX, name)
        if os.path.isdir(src) or name.startswith("."):
            if name.endswith(".icloud"):                    # not downloaded yet
                subprocess.run(["brctl", "download", src])
            continue
        if not name.lower().endswith(AUDIO):
            continue
        if not ensure_local(src):
            log(f"WAITING for iCloud to download {name}")
            continue
        if not stable(src):
            continue
        try:
            text = transcribe(src)
        except Exception as e:
            log(f"FAILED transcribe {name}: {e}")
            subprocess.run(["brctl", "download", src],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            continue

        label, rel = pick_destination(text, routes, special)
        routes, special = load_routes()                 # pick up any route just added
        dest = resolve(rel) if rel else None
        if not dest:
            label, dest = "unsorted", resolve(special.get("UNSORTED", ""))
        if not dest:
            log(f"FAILED no Drive folder for {name} (is Google Drive running?)")
            continue

        when = datetime.datetime.fromtimestamp(os.path.getmtime(src))
        safe = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        out = os.path.join(dest, f"{when:%Y-%m-%d %H%M} {safe}.txt")
        try:
            with open(out, "w") as f:
                f.write(text.strip() + "\n")
        except OSError as e:
            log(f"FAILED writing to Drive for {name}: {e}")
            continue
        shutil.move(src, os.path.join(DONE, name))
        log(f"OK {name} → [{label}] {out}")

if __name__ == "__main__":
    main()
