import re, html, json, os

SRC_MD   = "questions.md"   # edit this to change the questions, then re-run
OUT      = "index.html"

# Questions that get a file uploader under their box: code -> the fine print
# and the accept list for that particular ask.
ATTACH_TO = {
  "C1": ("spreadsheets, PDFs, decks, screenshots",
         ".xlsx,.xls,.csv,.numbers,.pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg,.heic,.txt,.zip"),
  "A3": ("SVG, EPS, AI, PDF, PNG &#8212; whatever you have",
         ".svg,.eps,.ai,.pdf,.png,.jpg,.jpeg,.webp,.zip"),
}
MAX_FILE_MB = 10            # per file; the backend enforces the same ceiling
MAX_FILES = 8               # across the whole form, not per uploader

TC_CSS = r'''
/* ==========================================================================
   TETHERED CREW - client intake sheet
   Working-drawing / spec-sheet system, locked to the light ("the print")
   theme. Tokens lifted from the Tethered Crew site so the two read as one
   piece of stationery.
   ========================================================================== */

:root {
  --ink: #15181B;
  --paper: #EDE8DC;
  --bg: #E7E9E6;
  --bg-raised: #F3F4F1;
  --write: #FBFBFA;
  --text: #1B1E22;
  --text-muted: #565C61;
  --text-faint: #8A9096;
  --accent: #3A5E82;
  --accent-strong: #2C4A68;
  --accent-wash: rgba(58, 94, 130, 0.08);
  --flag: #8C3547;
  --border: rgba(27, 30, 34, 0.14);
  --border-strong: rgba(27, 30, 34, 0.26);
  --shadow: 0 1px 2px rgba(21, 24, 27, 0.04), 0 12px 32px -16px rgba(21, 24, 27, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.65);

  --radius: 3px;
  --ease: cubic-bezier(0.22, 0.61, 0.36, 1);
  --measure: 66ch;

  --f-display: 'Fraunces', 'Iowan Old Style', Georgia, serif;
  --f-body: 'IBM Plex Sans', -apple-system, 'Segoe UI', Helvetica, sans-serif;
  --f-code: 'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace;
}

*, *::before, *::after { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--f-body);
  font-size: 17px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    transition-duration: 0.001ms !important;
  }
}

/* paper grain, same treatment as the site */
.grain {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 999;
  opacity: 0.035;
  mix-blend-mode: overlay;
  background-image:
    repeating-linear-gradient(0deg, var(--ink) 0px, transparent 1px, transparent 2px),
    repeating-linear-gradient(90deg, var(--ink) 0px, transparent 1px, transparent 2px);
  background-size: 3px 3px;
}

.sheet {
  max-width: 54rem;
  margin: 0 auto;
  padding: clamp(1.5rem, 4vw, 3.5rem) clamp(1rem, 4vw, 3rem) 4rem;
  display: flex;
  flex-direction: column;
  gap: clamp(2rem, 4vw, 3.25rem);
}

/* ---------- the mark ---------- */

.mark {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.mark-icon { width: 30px; height: 22px; overflow: visible; }
.mark-icon circle { stroke: var(--text); }
.mark-icon .ring-accent { stroke: url(#ringGradient); }

.mark-word {
  font-family: var(--f-display);
  font-size: 1.18rem;
  font-weight: 560;
  letter-spacing: -0.01em;
  color: var(--text);
}

/* ---------- masthead ---------- */

.masthead {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  border-bottom: 1px solid var(--border-strong);
  padding-bottom: 1.9rem;
}

.eyebrow {
  font-family: var(--f-code);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  align-items: center;
  margin-top: 0.6rem;
}

.eyebrow .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  display: inline-block;
}

h1 {
  font-family: var(--f-display);
  font-weight: 560;
  font-size: clamp(2.2rem, 5.4vw, 3.6rem);
  line-height: 1.04;
  letter-spacing: -0.01em;
  margin: 0;
  color: var(--text);
  text-wrap: balance;
}

.standfirst {
  margin: 0;
  max-width: var(--measure);
  font-size: 1.05rem;
  color: var(--text-muted);
}

.howto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin-top: 0.4rem;
}

.howto div { background: var(--bg-raised); padding: 1rem 1.1rem; }

.howto dt {
  font-family: var(--f-code);
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-faint);
  margin-bottom: 0.35rem;
}

.howto dd { margin: 0; font-size: 0.93rem; line-height: 1.5; color: var(--text-muted); }

.star { color: var(--accent); font-weight: 600; }

/* ---------- sections ---------- */

section { display: flex; flex-direction: column; gap: 1.5rem; }

.sec-head {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0 0.9rem;
  align-items: center;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.9rem;
}

.sec-letter {
  font-family: var(--f-code);
  font-weight: 600;
  font-size: 0.95rem;
  background: var(--accent);
  color: var(--bg-raised);
  padding: 0.34rem 0.66rem;
  border-radius: var(--radius);
  line-height: 1;
}

.sec-title {
  font-family: var(--f-display);
  font-weight: 560;
  font-size: clamp(1.35rem, 3vw, 1.8rem);
  letter-spacing: -0.01em;
  margin: 0;
  color: var(--text);
}

.sec-note {
  grid-column: 2;
  margin: 0.45rem 0 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  max-width: var(--measure);
}

/* ---------- questions ---------- */

.q {
  display: grid;
  grid-template-columns: 4rem 1fr;
  gap: 0 1rem;
  break-inside: avoid;
}

.q-code {
  font-family: var(--f-code);
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-faint);
  padding-top: 0.3rem;
}

.q-body { display: flex; flex-direction: column; gap: 0.5rem; min-width: 0; }

.q-text {
  margin: 0;
  font-size: 1.01rem;
  line-height: 1.5;
  color: var(--text);
  max-width: var(--measure);
  display: block;
  cursor: pointer;
}

.q-text .star { margin-right: 0.3rem; }

.q-hint {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--text-faint);
  max-width: var(--measure);
}

.answer,
textarea.answer {
  width: 100%;
  display: block;
  background: var(--write);
  border: 1px solid var(--border);
  border-left: 3px solid var(--border-strong);
  border-radius: var(--radius);
  min-height: 3.6rem;
  padding: 0.7rem 0.9rem;
  font-family: var(--f-body);
  font-size: 1rem;
  line-height: 1.65;
  color: var(--text);
  resize: vertical;
  overflow: hidden;
  outline: none;
  -webkit-appearance: none;
  transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease);
}

.answer.tall { min-height: 5.4rem; }

textarea.answer::placeholder { color: var(--text-faint); }

.answer:focus {
  border-left-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-wash);
}

.answer.missing { border-left-color: var(--flag); }

/* ---------- identity block ---------- */

.whois {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
  gap: 1rem;
}

.field { display: flex; flex-direction: column; gap: 0.35rem; }

.field label {
  font-family: var(--f-code);
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-faint);
}

.field input {
  font-family: var(--f-body);
  font-size: 1rem;
  padding: 0.62rem 0.8rem;
  background: var(--write);
  color: var(--text);
  border: 1px solid var(--border);
  border-left: 3px solid var(--border-strong);
  border-radius: var(--radius);
  outline: none;
  transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease);
}

.field input:focus {
  border-left-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-wash);
}

.field input.missing { border-left-color: var(--flag); }

/* honeypot */
.hp { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }

/* ---------- progress rail ---------- */

.progress {
  position: sticky;
  top: 0;
  z-index: 20;
  background: color-mix(in srgb, var(--bg) 92%, transparent);
  backdrop-filter: saturate(140%) blur(8px);
  -webkit-backdrop-filter: saturate(140%) blur(8px);
  border-bottom: 1px solid var(--border);
}

.progress-inner {
  max-width: 54rem;
  margin: 0 auto;
  padding: 0.7rem clamp(1rem, 4vw, 3rem);
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.progress-count {
  font-family: var(--f-code);
  font-size: 0.73rem;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.progress-track {
  flex: 1 1 8rem;
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  min-width: 6rem;
  overflow: hidden;
}

.progress-fill {
  display: block;
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--accent) 0%, var(--accent-strong) 100%);
  transition: width 0.3s var(--ease);
}

.sec-nav { display: flex; gap: 0.1rem; }

.sec-nav a {
  font-family: var(--f-code);
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--text-faint);
  text-decoration: none;
  padding: 0.24rem 0.44rem;
  border-radius: var(--radius);
  transition: color 0.2s var(--ease), background 0.2s var(--ease);
}

.sec-nav a:hover { color: var(--accent); background: var(--accent-wash); }
.sec-nav a.done { color: var(--accent); }

.saved-flag {
  font-family: var(--f-code);
  font-size: 0.67rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-faint);
  opacity: 0;
  transition: opacity 0.3s var(--ease);
  white-space: nowrap;
}

.saved-flag.show { opacity: 1; }

/* ---------- closer + actions ---------- */

.closer {
  background: var(--bg-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: clamp(1.4rem, 3vw, 2.2rem);
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.closer h2 {
  font-family: var(--f-display);
  font-weight: 560;
  font-size: clamp(1.5rem, 3.4vw, 2.1rem);
  letter-spacing: -0.01em;
  margin: 0;
  color: var(--text);
}

.closer p { margin: 0; max-width: var(--measure); color: var(--text-muted); }

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  margin-top: 0.6rem;
}

button {
  font-family: var(--f-body);
  font-weight: 500;
  font-size: 0.95rem;
  padding: 0.85rem 1.5rem;
  border-radius: var(--radius);
  border: 1px solid transparent;
  cursor: pointer;
  background: linear-gradient(160deg, #7C97B2 0%, var(--accent) 45%, var(--accent-strong) 100%);
  color: var(--bg-raised);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.4), inset 0 -2px 3px rgba(0,0,0,0.15), 0 1px 2px rgba(0,0,0,0.15);
  transition: transform 0.2s var(--ease), filter 0.2s var(--ease);
}

button:hover { transform: translateY(-1px); filter: brightness(1.06); }
button:active { transform: translateY(0); }

button.ghost {
  background: transparent;
  color: var(--text-muted);
  border-color: var(--border-strong);
  box-shadow: none;
}

button.ghost:hover { color: var(--accent); border-color: var(--accent); filter: none; }

button[disabled] { opacity: 0.55; cursor: progress; transform: none; }

.status { font-size: 0.9rem; color: var(--text-muted); }
.status.bad { color: var(--flag); }

/* ---------- done ---------- */

.done-panel { display: none; }
.done-panel.show { display: flex; flex-direction: column; gap: 1rem; }
body.submitted #intake { display: none; }
body.submitted .progress { display: none; }

/* ---------- footer ---------- */

.site-foot {
  max-width: 54rem;
  margin: 0 auto;
  padding: 1.6rem clamp(1rem, 4vw, 3rem) 3rem;
  border-top: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.site-foot .mark-icon circle { stroke: var(--text-muted); }
.site-foot .mark-word { color: var(--text-muted); font-size: 1rem; }

.foot-fine {
  margin: 0;
  font-family: var(--f-code);
  font-size: 0.72rem;
  color: var(--text-faint);
}

@media (max-width: 34rem) {
  .q { grid-template-columns: 1fr; gap: 0.35rem; }
  .q-code { padding-top: 0; }
  .sec-note { grid-column: 1 / -1; }
}

@media print {
  body { background: #fff; font-size: 11pt; }
  .grain, .progress, .actions, .saved-flag, .sec-nav { display: none; }
  .sheet { padding: 0; gap: 1.6rem; max-width: none; }
  .closer { box-shadow: none; }
  textarea.answer { overflow: visible; background: #fff; }
  .sec-head { break-after: avoid; }
}
'''

base_css = TC_CSS

# ---- parse the questionnaire source ----
sections, cur = [], None
for ln in open(SRC_MD).read().splitlines():
    m = re.match(r'^## ([A-Z])\. (.+)$', ln)
    if m:
        cur = {"letter": m.group(1), "title": m.group(2), "note": "", "qs": []}
        sections.append(cur); continue
    if ln.startswith("## Last one"):
        cur = {"letter": "H", "title": "One last one", "note": "", "qs": []}
        sections.append(cur); continue
    q = re.match(r'^([A-Z]\d+) (★ )?(.+)$', ln)
    if q and cur:
        code, star, text = q.group(1), bool(q.group(2)), q.group(3).strip()
        hint = ""
        hm = re.match(r'^(.*?) \(([^()]*)\)$', text)
        if hm and len(hm.group(2)) > 25:
            text, hint = hm.group(1).strip(), hm.group(2).strip()
        cur["qs"].append({"code": code, "star": star, "text": text, "hint": hint}); continue
    if cur and cur["letter"] == "H" and ln.strip() and not ln.startswith("Completed by"):
        cur["qs"].append({"code": "H1", "star": True, "text": ln.strip(), "hint": ""})

# section notes lifted from the printed sheet
NOTES = {
 "A": "The shape of the company. This decides what the system is even counting.",
 "B": "Logins and what each person is allowed to see. Easier to decide now than to unwind later.",
 "C": "Your pipeline in your own vocabulary, and the paperwork around it. We build the stages to match what you say here, not the other way around.",
 "D": "What this has to live alongside, and what's already been tried.",
 "W": "Only fill this in if a website is part of the job. It's optional \u2014 skip the whole section and nothing about the CRM changes.",
 "H": "",
}

# sections that are opt-in: hidden behind a toggle, excluded from the count
OPTIONAL = {"W"}
for s in sections:
    s["note"] = NOTES.get(s["letter"], "")

TITLES = {"A":"The business","B":"Who's in it","C":"How the work actually runs",
          "D":"Ground rules","W":"If you also want a website"}
for s in sections:
    s["title"] = TITLES.get(s["letter"], s["title"])
    s["optional"] = s["letter"] in OPTIONAL

# the counter and the progress bar only track the questions everyone answers
total_q = sum(len(s["qs"]) for s in sections if not s["optional"])
opt_codes = [q["code"] for s in sections if s["optional"] for q in s["qs"]]

# ---- markup ----
def esc(t): return html.escape(t, quote=True)

nav = "\n".join(
    f'      <a href="#sec-{s["letter"]}" data-sec="{s["letter"]}"'
    f'{" class=\"opt\"" if s["optional"] else ""}>{s["letter"]}</a>'
    for s in sections)

attach_json = json.dumps([c for c in ATTACH_TO])

def attach_html(code):
    fine, accept = ATTACH_TO[code]
    return f"""
        <div class="attach" data-attach="{code}">
          <input type="file" id="fileInput-{code}" multiple accept="{accept}">
          <div class="attach-drop" id="drop-{code}" tabindex="0" role="button"
            aria-label="Attach files, or drag them here">
            <svg class="attach-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
              <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5" fill="none" stroke-width="1.7"
                stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 15v3.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V15"
                fill="none" stroke-width="1.7" stroke-linecap="round"/>
            </svg>
            <span class="attach-copy">
              <strong>Attach the files</strong>
              <span class="attach-fine">Drag them here, or click to choose &#183;
                {fine} &#183; up to {MAX_FILE_MB}&#8239;MB each</span>
            </span>
          </div>
          <ul class="attach-list" id="fileList-{code}"></ul>
          <p class="attach-note" id="attachNote-{code}">Nothing here is shared with anyone. If a file
            is too big or won&#8217;t upload, answer in the box above and email it instead.</p>
        </div>"""

blocks = []
for s in sections:
    qs = []
    for q in s["qs"]:
        star = '<span class="star" title="Answer this one if you answer nothing else">&#9733;</span>' if q["star"] else ""
        hint = f'\n        <p class="q-hint">{esc(q["hint"])}</p>' if q["hint"] else ""
        tall = " tall" if q["hint"] or len(q["text"]) > 130 else ""
        attach = attach_html(q["code"]) if q["code"] in ATTACH_TO else ""
        qs.append(f"""    <div class="q">
      <div class="q-code">{q["code"]}</div>
      <div class="q-body">
        <label class="q-text" for="{q["code"]}">{star}{esc(q["text"])}</label>{hint}
        <textarea class="answer{tall}" id="{q["code"]}" name="{q["code"]}" rows="2"
          data-star="{str(q["star"]).lower()}" placeholder="Type your answer&#8230;"></textarea>{attach}
      </div>
    </div>""")
    note = f'\n      <p class="sec-note">{esc(s["note"])}</p>' if s["note"] else ""
    if s["optional"]:
        blocks.append(f"""  <section id="sec-{s['letter']}" class="optional">
    <div class="sec-head">
      <div class="sec-letter">{s['letter']}</div>
      <h2 class="sec-title">{esc(s['title'])} <span class="opt-tag">Optional</span></h2>{note}
    </div>

    <label class="opt-switch" for="wantSite">
      <input type="checkbox" id="wantSite">
      <span class="opt-box" aria-hidden="true"></span>
      <span class="opt-label">Yes &#8212; a website is part of this. Show me those questions.</span>
    </label>

    <div class="opt-body" id="siteQs" hidden>
{chr(10).join(qs)}
    </div>
  </section>""")
    else:
        blocks.append(f"""  <section id="sec-{s['letter']}">
    <div class="sec-head">
      <div class="sec-letter">{s['letter']}</div>
      <h2 class="sec-title">{esc(s['title'])}</h2>{note}
    </div>

{chr(10).join(qs)}
  </section>""")

extra_css = r'''
/* ---------- the optional section ---------- */

section.optional .sec-letter { background: var(--bg); color: var(--text-faint); border: 1px solid var(--border-strong); }

.opt-tag {
  font-family: var(--f-code);
  font-size: 0.6rem;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-faint);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  padding: 0.2rem 0.42rem;
  vertical-align: 0.28em;
  white-space: nowrap;
}

.opt-switch {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  cursor: pointer;
  padding: 0.85rem 1rem;
  background: var(--bg-raised);
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  max-width: var(--measure);
}

.opt-switch input { position: absolute; opacity: 0; width: 0; height: 0; }

.opt-box {
  flex: none;
  width: 1.05rem;
  height: 1.05rem;
  background: var(--write);
  border: 1px solid var(--border-strong);
  border-radius: 2px;
  position: relative;
  transition: background 0.15s var(--ease), border-color 0.15s var(--ease);
}

.opt-box::after {
  content: "";
  position: absolute;
  left: 0.32rem;
  top: 0.11rem;
  width: 0.28rem;
  height: 0.55rem;
  border: solid var(--bg-raised);
  border-width: 0 2px 2px 0;
  transform: rotate(42deg) scale(0.6);
  opacity: 0;
  transition: opacity 0.15s var(--ease), transform 0.15s var(--ease);
}

.opt-switch input:checked ~ .opt-box { background: var(--accent); border-color: var(--accent); }
.opt-switch input:checked ~ .opt-box::after { opacity: 1; transform: rotate(42deg) scale(1); }
.opt-switch input:focus-visible ~ .opt-box { box-shadow: 0 0 0 3px var(--accent-wash); }

.opt-label { font-size: 0.97rem; line-height: 1.45; color: var(--text-muted); }
.opt-switch input:checked ~ .opt-label { color: var(--text); }

.opt-body { display: flex; flex-direction: column; gap: 1.5rem; }
.opt-body[hidden] { display: none; }

/* ---------- file attachments ---------- */

.attach { display: flex; flex-direction: column; gap: 0.6rem; max-width: var(--measure); }
.attach input[type="file"] { position: absolute; opacity: 0; width: 0; height: 0; }

.attach-drop {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.85rem 1rem;
  background: var(--bg-raised);
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s var(--ease), background 0.15s var(--ease);
}

.attach-drop:hover,
.attach-drop:focus-visible,
.attach-drop.over { border-color: var(--accent); background: var(--accent-wash); }
.attach-drop.over { border-style: solid; }

.attach-icon { flex: none; width: 1.35rem; height: 1.35rem; stroke: var(--accent); }
.attach-copy { display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; }
.attach-copy strong { font-size: 0.95rem; font-weight: 560; color: var(--text); }

.attach-fine {
  font-size: 0.82rem;
  line-height: 1.4;
  color: var(--text-muted);
}

.attach-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.35rem; }

.attach-list li {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  gap: 0.7rem;
  padding: 0.5rem 0.7rem;
  background: var(--write);
  border: 1px solid var(--border);
  border-left: 3px solid var(--border-strong);
  border-radius: var(--radius);
  font-size: 0.88rem;
}

.attach-list li.done { border-left-color: var(--accent); }
.attach-list li.failed { border-left-color: var(--flag); }

.file-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text); }

.file-state {
  font-family: var(--f-code);
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-faint);
  white-space: nowrap;
}

.attach-list li.done .file-state { color: var(--accent); }
.attach-list li.failed .file-state { color: var(--flag); }

.file-drop {
  border: 0;
  background: none;
  padding: 0 0.2rem;
  font: inherit;
  font-size: 1.05rem;
  line-height: 1;
  color: var(--text-faint);
  cursor: pointer;
}

.file-drop:hover { color: var(--flag); }

.attach-note { margin: 0; font-size: 0.82rem; line-height: 1.45; color: var(--text-faint); }
.attach-note.bad { color: var(--flag); }

@media print { .attach-drop, .attach-note { display: none; } }

.sec-nav a.opt { color: var(--text-faint); }
.sec-nav a.opt.done { color: var(--accent); }

@media print { .opt-switch { border-style: solid; background: #fff; } }
'''

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Client Questionnaire</title>
<meta name="description" content="A short questionnaire so what we build gets built around how you actually work.">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400..700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
{base_css}
{extra_css}
</style>
</head>
<body>

<div class="grain" aria-hidden="true"></div>

<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="ringGradient" x1="10%" y1="0%" x2="90%" y2="100%">
      <stop offset="0%" stop-color="#B0BECD"/>
      <stop offset="50%" stop-color="#3A5E82"/>
      <stop offset="100%" stop-color="#2C4A68"/>
    </linearGradient>
  </defs>
</svg>

<div class="progress">
  <div class="progress-inner">
    <span class="progress-count"><span id="answered">0</span> / {total_q} answered</span>
    <span class="progress-track"><span class="progress-fill" id="bar"></span></span>
    <nav class="sec-nav" aria-label="Jump to section">
{nav}
    </nav>
    <span class="saved-flag" id="savedFlag">Saved</span>
  </div>
</div>

<form class="sheet" id="intake" novalidate>

  <header class="masthead">
    <div class="mark">
      <svg class="mark-icon" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
        <circle cx="12" cy="16" r="8.5" fill="none" stroke-width="2.25"/>
        <circle cx="20" cy="16" r="8.5" fill="none" stroke-width="2.25" class="ring-accent"/>
      </svg>
      <span class="mark-word">Tethered&nbsp;Crew</span>
    </div>
    <div class="eyebrow"><span class="dot"></span> Discovery &nbsp;&#183;&nbsp; Tethered Crew</div>
    <h1>Client questionnaire</h1>
    <p class="standfirst">Everything below exists so the system gets built around how you actually work &mdash; your stages, your line-review calendar, the software you won't give up &mdash; instead of a generic sales pipeline you'd have to fight. Short answers are fine. &ldquo;I don't know yet&rdquo; is a real answer and tells us something too.</p>
    <dl class="howto">
      <div>
        <dt>Who fills this out</dt>
        <dd>Whoever runs the day-to-day. Pull in a rep for Section C if they know the workflow better.</dd>
      </div>
      <div>
        <dt>How long it takes</dt>
        <dd>About ten minutes. It's deliberately short &mdash; every question here changes something we'd build.</dd>
      </div>
      <div>
        <dt>You can stop anytime</dt>
        <dd>Your answers save in this browser as you type. Close the tab, come back later, pick up where you left off.</dd>
      </div>
    </dl>
  </header>

  <section>
    <div class="sec-head">
      <div class="sec-letter">&#8212;</div>
      <h2 class="sec-title">First, who are you</h2>
    </div>
    <div class="whois">
      <div class="field">
        <label for="_name">Your name</label>
        <input type="text" id="_name" name="_name" autocomplete="name" required>
      </div>
      <div class="field">
        <label for="_company">Company</label>
        <input type="text" id="_company" name="_company" autocomplete="organization" required>
      </div>
      <div class="field">
        <label for="_email">Email</label>
        <input type="email" id="_email" name="_email" autocomplete="email" required>
      </div>
    </div>
    <div class="hp" aria-hidden="true">
      <label for="_website">Leave this field empty</label>
      <input type="text" id="_website" name="_website" tabindex="-1" autocomplete="off">
    </div>
  </section>

{chr(10).join(blocks)}

  <div class="closer">
    <h2>That's everything</h2>
    <p>Send it over and we'll read it before we talk. If something didn't fit in a box &mdash; a report, a deck, a screenshot of the thing that drives you crazy &mdash; attach it up at C1 or email it along, and it'll get used.</p>
    <div class="actions">
      <button type="submit" id="submitBtn">Send my answers</button>
      <button type="button" class="ghost" id="copyBtn">Save a copy</button>
      <span class="status" id="status"></span>
    </div>
  </div>

</form>

<div class="sheet done-panel" id="donePanel">
  <div class="closer">
    <div class="eyebrow"><span class="dot"></span> Received</div>
    <h2>Got it &mdash; thank you.</h2>
    <p>Your answers are in. We'll read through them and come back to you with what we'd build first and what it takes to get there.</p>
    <p>If you remembered something after hitting send, just reply to the email &mdash; no need to fill this out again.</p>
  </div>
</div>

<script>
/* ------------------------------------------------------------------
   CONFIG - paste your Apps Script Web App URL between the quotes.
   See README.md for the two-minute setup.
------------------------------------------------------------------ */
var ENDPOINT = "https://script.google.com/macros/s/AKfycbzeNeSs0bf-UC0C9vym-jyMENgVFsD5tV6tv7pubXslolGZh3LqJ2bBMDJYFZ3vpPFg/exec";
/* ---------------------------------------------------------------- */

var form   = document.getElementById('intake');
var fields = Array.prototype.slice.call(form.querySelectorAll('textarea, input'));
fields = fields.filter(function (f) {{ return f.name !== '_website' && f.id !== 'wantSite'; }});
var OPTIONAL_CODES = {json.dumps(opt_codes)};
var qFields = fields.filter(function (f) {{
  return f.tagName === 'TEXTAREA' && OPTIONAL_CODES.indexOf(f.name) === -1;
}});
var wantSite = document.getElementById('wantSite');
var siteQs   = document.getElementById('siteQs');
var KEY = 'crm-intake-v1';

/* ---- autosize ---- */
function autosize(el) {{
  el.style.height = 'auto';
  el.style.height = Math.max(el.scrollHeight, 56) + 'px';
}}

/* ---- restore ---- */
function restore() {{
  var raw;
  try {{ raw = localStorage.getItem(KEY); }} catch (e) {{ return; }}
  if (!raw) return;
  var data;
  try {{ data = JSON.parse(raw); }} catch (e) {{ return; }}
  fields.forEach(function (f) {{
    if (data[f.name]) f.value = data[f.name];
  }});
  if (wantSite && data.__wantSite) wantSite.checked = true;
}}

/* ---- save ---- */
var saveTimer = null;
var flag = document.getElementById('savedFlag');

function save() {{
  var data = {{}};
  fields.forEach(function (f) {{ if (f.value.trim()) data[f.name] = f.value; }});
  if (wantSite && wantSite.checked) data.__wantSite = true;
  if (typeof uploads !== 'undefined' && uploads.length) {{
    data.__files = uploads.filter(function (u) {{ return u.state === 'done'; }});
  }}
  try {{ localStorage.setItem(KEY, JSON.stringify(data)); }} catch (e) {{ return; }}
  flag.classList.add('show');
  clearTimeout(saveTimer);
  saveTimer = setTimeout(function () {{ flag.classList.remove('show'); }}, 1200);
}}

/* ---- progress ---- */
var answeredEl = document.getElementById('answered');
var bar = document.getElementById('bar');
var navLinks = Array.prototype.slice.call(document.querySelectorAll('.sec-nav a'));

function tally() {{
  var n = qFields.filter(function (f) {{ return f.value.trim(); }}).length;
  answeredEl.textContent = n;
  bar.style.width = (n / {total_q} * 100) + '%';
  navLinks.forEach(function (a) {{
    var sec = document.getElementById('sec-' + a.dataset.sec);
    if (!sec) return;
    var tas = Array.prototype.slice.call(sec.querySelectorAll('textarea'));
    var skip = sec.classList.contains('optional') && (!wantSite || !wantSite.checked);
    var filled = tas.filter(function (t) {{ return t.value.trim(); }}).length;
    a.classList.toggle('done', !skip && filled === tas.length && tas.length > 0);
  }});
}}

/* ---- optional section ---- */
function syncSite() {{
  if (!wantSite || !siteQs) return;
  siteQs.hidden = !wantSite.checked;
  if (wantSite.checked) {{
    Array.prototype.slice.call(siteQs.querySelectorAll('textarea')).forEach(autosize);
  }}
}}

if (wantSite) {{
  wantSite.addEventListener('change', function () {{
    syncSite();
    save();
    tally();
    if (wantSite.checked) {{
      siteQs.querySelector('textarea').focus({{ preventScroll: true }});
    }}
  }});
}}

/* ---- wire up ---- */
restore();
syncSite();
qFields.forEach(autosize);
tally();

fields.forEach(function (f) {{
  f.addEventListener('input', function () {{
    if (f.tagName === 'TEXTAREA') autosize(f);
    f.classList.remove('missing');
    save();
    tally();
  }});
}});

/* ---- attachments ----------------------------------------------
   Each file is uploaded on its own request as soon as it's picked, so
   a big spreadsheet can't take the answers down with it. What travels
   with the answers is just a list of Drive links.
------------------------------------------------------------------ */
var MAX_BYTES = {MAX_FILE_MB} * 1024 * 1024;
var MAX_FILES = {MAX_FILES};
var ATTACH_QS = {attach_json};
var uploads = [];                       /* {{ q, name, size, url, state }} */
(function restoreFiles() {{
  var raw;
  try {{ raw = localStorage.getItem(KEY); }} catch (e) {{ return; }}
  if (!raw) return;
  try {{ uploads = (JSON.parse(raw).__files || []).slice(0, MAX_FILES); }} catch (e) {{}}
}})();

function human(bytes) {{
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
  return (bytes / 1024 / 1024).toFixed(1) + ' MB';
}}

var STATE_WORDS = {{ uploading: 'Sending', done: 'Attached', failed: 'Failed' }};
var zones = {{}};

function noteBad(code, msg) {{
  var z = zones[code];
  if (!z) return;
  z.note.textContent = msg;
  z.note.className = 'attach-note bad';
}}

function noteReset(code) {{
  var z = zones[code];
  if (!z) return;
  z.note.innerHTML = z.noteDefault;
  z.note.className = 'attach-note';
}}

function renderFiles() {{
  ATTACH_QS.forEach(function (code) {{
    var z = zones[code];
    if (!z) return;
    z.list.innerHTML = '';
    uploads.forEach(function (u) {{
      if (u.q !== code) return;
      var li = document.createElement('li');
      li.className = u.state;

      var name = document.createElement('span');
      name.className = 'file-name';
      name.textContent = u.name + '  \u00b7  ' + human(u.size);

      var state = document.createElement('span');
      state.className = 'file-state';
      state.textContent = STATE_WORDS[u.state] || u.state;

      var x = document.createElement('button');
      x.type = 'button';
      x.className = 'file-drop';
      x.setAttribute('aria-label', 'Remove ' + u.name);
      x.textContent = '\u00d7';
      x.addEventListener('click', function () {{
        var at = uploads.indexOf(u);
        if (at > -1) uploads.splice(at, 1);
        renderFiles();
        save();
      }});

      li.appendChild(name); li.appendChild(state); li.appendChild(x);
      z.list.appendChild(li);
    }});
  }});
}}

function uploadFile(code, file) {{
  var entry = {{ q: code, name: file.name, size: file.size, url: '', state: 'uploading' }};
  uploads.push(entry);
  renderFiles();

  var reader = new FileReader();
  reader.onerror = function () {{
    entry.state = 'failed';
    renderFiles();
    noteBad(code, 'Couldn’t read ' + file.name + '. Email that one instead.');
  }};
  reader.onload = function () {{
    var b64 = String(reader.result).split(',')[1] || '';
    fetch(ENDPOINT, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
      body: JSON.stringify({{
        _kind: 'file',
        _company: form._company.value,
        _name: form._name.value,
        question: code,
        filename: file.name,
        mimeType: file.type || 'application/octet-stream',
        data: b64
      }})
    }})
      .then(function (r) {{ return r.json(); }})
      .then(function (res) {{
        if (!res || !res.ok || !res.url) throw new Error('rejected');
        entry.url = res.url;
        entry.state = 'done';
        renderFiles();
        save();
      }})
      .catch(function () {{
        entry.state = 'failed';
        renderFiles();
        noteBad(code, file.name + ' didn’t upload. Send that one by email \u2014 everything else is fine.');
      }});
  }};
  reader.readAsDataURL(file);
}}

function addFiles(code, list) {{
  noteReset(code);
  Array.prototype.slice.call(list).forEach(function (file) {{
    if (uploads.length >= MAX_FILES) {{
      noteBad(code, 'That’s ' + MAX_FILES + ' files \u2014 the limit across the whole form. Email any others along.');
      return;
    }}
    if (file.size > MAX_BYTES) {{
      noteBad(code, file.name + ' is ' + human(file.size) + '. The limit here is {MAX_FILE_MB} MB \u2014 email that one instead.');
      return;
    }}
    uploadFile(code, file);
  }});
}}

ATTACH_QS.forEach(function (code) {{
  var drop  = document.getElementById('drop-' + code);
  var input = document.getElementById('fileInput-' + code);
  var list  = document.getElementById('fileList-' + code);
  var note  = document.getElementById('attachNote-' + code);
  if (!drop || !input || !list || !note) return;

  zones[code] = {{ drop: drop, input: input, list: list, note: note, noteDefault: note.innerHTML }};

  drop.addEventListener('click', function () {{ input.click(); }});
  drop.addEventListener('keydown', function (e) {{
    if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); input.click(); }}
  }});
  input.addEventListener('change', function () {{
    addFiles(code, input.files);
    input.value = '';
  }});
  ['dragenter', 'dragover'].forEach(function (ev) {{
    drop.addEventListener(ev, function (e) {{ e.preventDefault(); drop.classList.add('over'); }});
  }});
  ['dragleave', 'drop'].forEach(function (ev) {{
    drop.addEventListener(ev, function (e) {{ e.preventDefault(); drop.classList.remove('over'); }});
  }});
  drop.addEventListener('drop', function (e) {{
    if (e.dataTransfer && e.dataTransfer.files) addFiles(code, e.dataTransfer.files);
  }});
}});

renderFiles();

/* ---- plain-text transcript ---- */
function transcript() {{
  var out = ['CLIENT QUESTIONNAIRE \\u2014 answers', ''];
  out.push('Name:    ' + form._name.value);
  out.push('Company: ' + form._company.value);
  out.push('Email:   ' + form._email.value);
  if (typeof uploads !== 'undefined') {{
    var sent = uploads.filter(function (u) {{ return u.state === 'done'; }});
    if (sent.length) {{
      out.push('');
      out.push('Files attached: ' + sent.map(function (u) {{ return u.name; }}).join(', '));
    }}
  }}
  out.push('');
  document.querySelectorAll('form section').forEach(function (sec) {{
    if (sec.classList.contains('optional') && (!wantSite || !wantSite.checked)) return;
    var t = sec.querySelector('.sec-title');
    var tas = sec.querySelectorAll('textarea');
    if (!tas.length) return;
    out.push('=== ' + t.textContent.toUpperCase() + ' ===', '');
    tas.forEach(function (ta) {{
      var label = sec.querySelector('label[for="' + ta.name + '"]');
      out.push(ta.name + '. ' + (label ? label.textContent.trim() : ''));
      out.push(ta.value.trim() ? ta.value.trim() : '(no answer)');
      out.push('');
    }});
  }});
  return out.join('\\n');
}}

document.getElementById('copyBtn').addEventListener('click', function () {{
  var blob = new Blob([transcript()], {{ type: 'text/plain' }});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'client-questionnaire-' + (form._company.value.replace(/[^a-z0-9]+/gi, '-').toLowerCase() || 'answers') + '.txt';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}});

/* ---- submit ---- */
var status = document.getElementById('status');
var btn = document.getElementById('submitBtn');

form.addEventListener('submit', function (e) {{
  e.preventDefault();

  var required = [form._name, form._company, form._email];
  var missing = required.filter(function (f) {{ return !f.value.trim(); }});
  missing.forEach(function (f) {{ f.classList.add('missing'); }});
  if (missing.length) {{
    status.textContent = 'Add your name, company, and email at the top first.';
    status.className = 'status bad';
    missing[0].focus();
    missing[0].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    return;
  }}

  if (uploads.some(function (u) {{ return u.state === 'uploading'; }})) {{
    status.className = 'status bad';
    status.textContent = 'A file is still uploading \\u2014 give it a second.';
    return;
  }}

  if (form._website.value) {{           // honeypot: only a bot fills this
    document.body.classList.add('submitted');
    document.getElementById('donePanel').classList.add('show');
    return;
  }}

  var wantsSite = !!(wantSite && wantSite.checked);
  var attached = uploads.filter(function (u) {{ return u.state === 'done'; }});
  var payload = {{
    _submittedAt: new Date().toISOString(),
    _wantsWebsite: wantsSite ? 'Yes' : 'No',
    _files: attached.map(function (u) {{ return {{ q: u.q, name: u.name, url: u.url }}; }}),
    _transcript: transcript()
  }};
  fields.forEach(function (f) {{
    if (!wantsSite && OPTIONAL_CODES.indexOf(f.name) !== -1) return;
    payload[f.name] = f.value.trim();
  }});

  btn.disabled = true;
  status.className = 'status';
  status.textContent = 'Sending\\u2026';

  fetch(ENDPOINT, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
    body: JSON.stringify(payload)
  }})
    .then(function (r) {{ return r.text(); }})
    .then(function () {{
      try {{ localStorage.removeItem(KEY); }} catch (e) {{}}
      document.body.classList.add('submitted');
      document.getElementById('donePanel').classList.add('show');
      window.scrollTo(0, 0);
    }})
    .catch(function () {{
      btn.disabled = false;
      status.className = 'status bad';
      status.innerHTML = 'That didn\\'t send. Click <strong>Save a copy</strong> and reply to the email that sent you this link with the file attached \\u2014 nothing you typed is lost.';
    }});
}});
</script>

<footer class="site-foot">
  <div class="mark">
    <svg class="mark-icon" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <circle cx="12" cy="16" r="8.5" fill="none" stroke-width="2.25"/>
      <circle cx="20" cy="16" r="8.5" fill="none" stroke-width="2.25" class="ring-accent"/>
    </svg>
    <span class="mark-word">Tethered&nbsp;Crew</span>
  </div>
  <p class="foot-fine">Websites, CRMs, and operations built as one system.</p>
</footer>

</body>
</html>
"""

if os.path.dirname(OUT):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(doc)
print("wrote", OUT, "|", total_q, "questions,", len(sections), "sections")
