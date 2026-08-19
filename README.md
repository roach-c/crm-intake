# CRM Discovery Questionnaire — self-hosted

A single static page that asks a prospective CRM client 41 questions, saves
their progress as they type, and sends the answers to a Google Sheet + your
inbox. Runs on GitHub Pages (or any static host). No form service, no monthly
cost, no third-party account beyond the Google one you already have.

```
index.html   the form — the only file that gets published
Code.gs      the backend — lives in Google Apps Script, not on the site
```

---

## Why it needs a backend at all

GitHub Pages only serves files. It can't receive a form submission, so the
answers need somewhere to go. `Code.gs` is that somewhere: a Google Apps Script
web app that takes the POST, appends a row to a Sheet, and emails you a
readable copy. It's free and it's yours.

---

## Setup

### 1. Stand up the backend (~2 minutes)

1. Create a new Google Sheet — name it whatever you want.
2. In that Sheet: **Extensions → Apps Script**.
3. Delete the stub code, paste in all of `Code.gs`.
4. Change `NOTIFY_EMAIL` at the top to the address that should get submissions.
5. **Deploy → New deployment → Web app**
   - Execute as: **Me**
   - Who has access: **Anyone** ← required. Visitors aren't signed in to Google,
     so "Anyone with a Google account" will silently fail.
6. Approve the permission prompt, then copy the **Web app URL**.

Sanity check: paste that URL into a browser tab. You should see
`{"ok":true,"message":"Questionnaire endpoint is live."}`. You can also run
`testRun` from the Apps Script editor to confirm the Sheet write and the email.

### 2. Point the form at it

In `index.html`, near the bottom:

```js
var ENDPOINT = "PASTE_YOUR_APPS_SCRIPT_URL_HERE";
var FALLBACK_EMAIL = "you@yourdomain.com";
```

`ENDPOINT` is the Web app URL from step 1.

`FALLBACK_EMAIL` only ever appears if a submission fails to send — the page
tells them to download their answers and email them to you instead. It renders
in public HTML, so use a business address, not a personal one.

### 3. Publish

```bash
cd "crm-intake-form"
git init
git add index.html README.md          # do NOT commit Code.gs secrets if you add any
git commit -m "CRM discovery questionnaire"
gh repo create crm-intake --public --source=. --push
```

Then in the repo: **Settings → Pages → Source: main / root**. A minute later
it's at `https://<user>.github.io/crm-intake/`.

For a custom domain (`intake.yourdomain.com`), add a `CNAME` file containing
that hostname and point a CNAME DNS record at `<user>.github.io`.

---

## Redeploying after an edit

Editing `Code.gs` in the Apps Script editor does **not** update the live
endpoint. You have to **Deploy → Manage deployments → edit → New version**.
This catches everybody once.

---

## What the person filling it out gets

- Progress bar and section jump links at the top
- Answers autosave to their browser as they type — they can close the tab and
  come back; nothing is lost
- A **Save a copy** button that downloads their answers as a text file
- Stars marking the 21 questions that matter most, so a 15-minute pass is viable
- If the send fails, a clear recovery path instead of a lost hour of typing

## What you get

- One row per submission on the Sheet, one column per question code
- An email with only the answered questions, formatted to actually read,
  with reply-to set to the person who filled it out

---

## Changing the questions

`index.html` is generated but perfectly editable by hand. If you add or remove
a question, keep the `id`/`name` on the textarea matching its code (`D8`, etc.)
and add that same code to the `CODES` and `LABELS` lists in `Code.gs` so the
column lines up.
