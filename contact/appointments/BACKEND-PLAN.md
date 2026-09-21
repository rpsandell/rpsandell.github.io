# Appointment system — backend plan (LRZ webhosting)

*Status 2026-09-21. The front-end in this folder is complete and runs in preview
mode. The backend described here is to be built once the Funktionskennung and the
LRZ website exist. This document is the specification and the application checklist.*

## 1. Decision and why

The backend runs on **LRZ standard webhosting** (Apache + PHP-FPM + MySQL, Debian),
owned by a **Funktionskennung**. Cloudflare and every other external provider are out.

What this buys:

- **All personal data stays inside the Münchner Wissenschaftsnetz.** Requesters'
  names, addresses, messages and PDFs are stored on LRZ systems and mailed through
  LRZ's own servers. Nothing crosses to a US provider. This is the cleanest possible
  position for the Datenschutzbeauftragte/r.
- **The credential question disappears.** PHP on LRZ webhosting runs *as the
  Funktionskennung* (PHP-FPM). A config file holding its SMTP password, readable only
  by that account and stored outside the document root, is precisely the arrangement
  the LRZ-Passwortrichtlinie permits for Funktionskennungen (Verbindliche Anmerkung 2:
  "…Speicherung z. B. in Skripten für Web-Anwendungen … zulässig … strikte
  Zugriffsbeschränkung im Dateisystem"). No personal Kennung is involved anywhere.
- **Mail comes from a real MWN address.** LRZ requires the sender to be a working
  MWN address and forbids external domains — which is exactly what we want. Sent via
  authenticated SMTP from inside the MWN, it will be fully authenticated and reach
  `lrz.uni-muenchen.de` and `campus.lmu.de` inboxes without spam-filter trouble.

## 2. Where the booking page itself should live

Two workable layouts. **Recommendation: (B).**

**(A) Page on GitHub Pages, backend on LRZ.** The form at
`rpsandell.github.io/contact/appointments/` POSTs across origins to the LRZ site.
Works; needs a CORS header on the PHP side allowing only `https://rpsandell.github.io`.
The form data never touches GitHub, but the page is served from a US CDN.

**(B) Page and backend both on the LRZ site.** The Contact page on GitHub simply links
to `https://<lrz-site>/`. Same origin → no CORS, simpler, and the *entire* flow —
page, submission, storage, mail — is inside the MWN, which is a one-sentence answer
for the DSB. The front-end already built here is plain HTML/CSS/JS and moves over
unchanged. This repository stays the versioned source of the page; deploying is a
copy (§ 7).

## 3. What to ask LRZ for — the application checklist

Two requests, in this order. The **DNS name** is the long pole ("mehrere Tage bis
Wochen" — needs LMU's approval), so start it first.

**Request 1 — Funktionskennung** (via your Master User / LMU-Benutzerverwaltung):

- Purpose: "Terminbuchungssystem für Sprechstunden / Beratungsgespräche (Webanwendung)".
- **With a mailbox / e-mail address.** This address becomes the `From:` of every
  automated mail (e.g. `termine.sandell@lrz.uni-muenchen.de` or whatever LRZ assigns).
  Your personal LRZ address goes in `Reply-To:`, so replies land in your inbox.
- Mention § 4 Abs. 8 Benutzungsrichtlinien: this is a Vorhaben zur Verarbeitung
  personenbezogener Daten (names, e-mail addresses, free text, uploaded PDFs of
  students and external requesters), stored in the site's MySQL DB and filesystem,
  deleted 30 days after the appointment. Asking them to note it now closes that
  obligation in the same ticket.

**Request 2 — Website** (LRZ-Servicedesk, authenticated submit), once the
Funktionskennung exists. The form asks for exactly these; have answers ready:

| Field | Answer |
|---|---|
| LRZ-Funktionskennung | the one from Request 1 |
| DNS-Name | a name under an LMU domain — coordinate with your institute's IT / LMU DNS; e.g. `termine.<institut>.lmu.de`. Needs LMU sign-off. |
| Alias-Namen | none needed |
| Organisation | LMU, Institut für Vergleichende und Historische Sprachwissenschaft sowie Albanologie |
| MySQL-Datenbank | **yes** |
| PHP-Version | **8.3 or newer** (8.2 is default; 8.3–8.5 on request) |

Add to the free-text of that request — these aren't on the form but decide the design:

1. **Upload limit.** "Die Anwendung nimmt PDF-Uploads bis 50 MB entgegen. Sind
   `upload_max_filesize` und `post_max_size` per `.user.ini` auf 64M setzbar, oder
   können Sie das für die Site konfigurieren?" (PHP-FPM normally honours `.user.ini`
   for these two directives; if not, the fallback is chunked upload — § 5.4.)
2. **SMTP.** Confirm the site may send via `postout.lrz.de` (587/STARTTLS) authenticated
   with the Funktionskennung, `From:` = its mailbox address. Expected volume: well
   under 50 mails/day (three per booking).
3. **Cron.** Confirm cron jobs are enabled for the site (needed for hold-expiry and
   the 30-day deletion; both run every 15 min / nightly).
4. **Certificate.** Confirm the DNS name will be in the server certificate (HTTPS).

## 4. Data protection — what to tell the DSB

One paragraph they can file:

> Ein Web-Formular auf LRZ-Webhosting nimmt Terminanfragen entgegen. Verarbeitet
> werden Name, E-Mail-Adresse, gewähltes Thema, Terminzeit, Format (persönlich/Zoom),
> optional eine Freitext-Nachricht und optional bis zu drei PDF-Dateien (≤ 50 MB).
> Rechtsgrundlage Art. 6 Abs. 1 lit. b DSGVO (Terminvereinbarung auf Anfrage der
> betroffenen Person). Speicherung ausschließlich in der MySQL-Datenbank und im
> Dateisystem der LRZ-Site; Übermittlung ausschließlich per E-Mail über LRZ-Mailserver
> an den Anfragenden und an mich. Keine Weitergabe an Dritte, keine Verarbeitung
> außerhalb des MWN, keine Cookies/Tracking. Automatische Löschung aller Daten 30 Tage
> nach dem Termin bzw. nach Ablehnung/Verfall der Anfrage. Betroffenenrechte per
> E-Mail an ryan.sandell@lrz.uni-muenchen.de. Nicht vorgesehen: besondere Kategorien
> nach Art. 9 DSGVO; die Datenschutzhinweise bitten darum, keine Gesundheitsdaten o. ä.
> anzugeben.

Note LRZ webhosting explicitly does **not** offer special handling for Art. 9 data,
hence the last sentence — the privacy notice on the page now carries that request.

## 5. Backend specification

Plain PHP 8.3, no framework. One Composer dependency: **PHPMailer** (LRZ's own
recommendation for SMTP). Everything else is standard library. Roughly 600–800 lines.

### 5.1 Layout on the LRZ site

```
<site root>/
  config.php              secrets: DB + SMTP password  — OUTSIDE the document root, mode 0600
  storage/uploads/        PDFs, one folder per request  — OUTSIDE the document root
  htdocs/                 document root
    index.html            the booking page (from this repo)
    submitted/index.html
    availability.json     ← the file you edit
    assets/               appointments.css/js + fonts + site.css
    api/
      request.php         POST: validate, store, hold slot, mail Ryan
      taken.php           GET: JSON list of held/booked slots (start, minutes) — nothing else
      decide.php          GET: shows Approve / Deny page for a token; POST: acts on it
      file.php            GET: serves an uploaded PDF to a valid decision token only
    cron/
      expire.php          every 15 min: release holds past holdHours, mail requester
      purge.php           nightly: delete rows + files past delete_after
  vendor/                 PHPMailer (Composer)
```

### 5.2 Database (MySQL)

```sql
requests (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  token_hash    CHAR(64) NOT NULL UNIQUE,      -- sha256 of the random link token
  status        ENUM('pending','approved','denied','expired') NOT NULL,
  lang          CHAR(2) NOT NULL,              -- 'de' | 'en' — which language to mail in
  topic_id      VARCHAR(40) NOT NULL,
  format        VARCHAR(20) NOT NULL,          -- 'in-person' | 'zoom'
  start_local   DATETIME NOT NULL,             -- Europe/Berlin wall clock
  minutes       SMALLINT NOT NULL,
  name          VARCHAR(200) NOT NULL,
  email         VARCHAR(254) NOT NULL,
  message       TEXT,
  ip_hash       CHAR(64),                      -- salted, for rate limiting only
  created_at    DATETIME NOT NULL,
  hold_until    DATETIME NOT NULL,             -- created_at + holdHours
  decided_at    DATETIME,
  deny_reason   VARCHAR(30),                   -- 'unavailable' | 'wrong-contact' | 'need-info'
  deny_note     TEXT,
  delete_after  DATETIME NOT NULL              -- appointment + 30 d, or decision + 30 d
);
files (
  id INT AUTO_INCREMENT PRIMARY KEY, request_id INT NOT NULL,
  original_name VARCHAR(255), stored_name VARCHAR(80), bytes INT, sha256 CHAR(64)
);
```

A slot is "taken" if a row with `status IN ('pending','approved')` overlaps it. Slot
uniqueness is enforced in the DB transaction on insert (re-check overlap inside
`SELECT … FOR UPDATE`), so two simultaneous requests cannot both hold the same time —
the second gets HTTP 409 and the page tells them to pick another.

### 5.3 The flows

**Request** (`request.php`) — validate every field server-side against
`availability.json` (topic exists, minutes match, slot inside a window, after
`leadHours`, before `horizonDays`, not blocked, not overlapping); honeypot field must
be empty; ≤ 5 requests per IP-hash per hour; PDFs: magic bytes `%PDF-`, ≤ 50 MB, ≤ 3.
Insert row + files. Mail **Ryan** (in German): all details, links to each PDF, and
one link → `decide.php?t=<token>`. Redirect the browser to `submitted/`.

**Decision page** (`decide.php`, GET) — validates the token, shows the request and two
buttons. It acts only on **POST**: mail-security scanners pre-fetch links in incoming
mail, so a GET must never approve anything.
- **Approve** → status `approved`; mail the requester (their language) with date, time,
  length, format, your office address *or* your Zoom link, and an `.ics` attachment;
  mail you a second confirmation with the same `.ics`. Slot stays taken.
- **Deny** → a radio choice of the three reasons plus an optional free-text line →
  status `denied`; mail the requester the matching template. Slot released.
  1. *Termin nicht mehr verfügbar* — invites them to pick another time (link back).
  2. *Ich bin nicht der richtige Ansprechpartner* — optional note naming who is.
  3. *Ich benötige weitere Informationen* — asks them to reply by e-mail; **holds the
     slot** for a further `holdHours` so it isn't lost while they answer.
Tokens are single-use (row status changes) and die with `hold_until`.

**Expiry** (`cron/expire.php`, every 15 min) — pending rows past `hold_until` →
`expired`; mail the requester that the request lapsed and invite a new one.

**Purge** (`cron/purge.php`, nightly) — delete rows and their upload folders past
`delete_after`. This is the 30-day promise in the privacy notice, enforced by code.

**Taken** (`taken.php`) — returns only `[{start, minutes}]` for pending/approved rows
inside the horizon. No names, no topics; nothing a visitor shouldn't see.

### 5.4 Uploads

Preferred: `.user.ini` in `htdocs/` with `upload_max_filesize=64M`, `post_max_size=200M`.
If LRZ's answer to checklist item 1 is no, the front-end switches to **chunked upload**
(2 MB pieces, reassembled by `request.php`) — a contained change in `appointments.js`
and one extra endpoint, and no dependence on server limits at all.

### 5.5 Mail

PHPMailer → `postout.lrz.de:587`, STARTTLS, auth = Funktionskennung. `From:` = the
Funktionskennung's address; `Reply-To:` = `ryan.sandell@lrz.uni-muenchen.de`. All
templates in one PHP file, German and English side by side, plain text (+ `.ics` as
`text/calendar` attachment on confirmations). Templates are the next thing we write
together, along with the topic list.

### 5.6 Security notes

- Config outside the document root; `chmod 600`; owned by the Funktionskennung.
- Uploads outside the document root; served only through `file.php` to a valid token.
- Prepared statements everywhere; all output HTML-escaped; `SameSite` not needed
  (no cookies at all).
- Token: 32 random bytes, base64url; only its SHA-256 is stored.
- Rate limiting by salted IP hash, which is also purged nightly.

## 6. Open items (decisions still with Ryan)

1. Topic list and per-topic lengths (placeholders in `availability.json`).
2. Wording of all five e-mails (to Ryan; approved; denied ×3) and the expiry notice.
3. Office address for in-person confirmations; Zoom link (personal room or per-meeting).
4. The response-time promise on the landing page ("within two working days").
5. Final privacy-notice text — reviewed by the DSB.
6. Whether requesters must confirm their e-mail address before the request reaches
   you (double opt-in). Not planned; a cheap upgrade if spam ever becomes a problem.

## 7. Deploying the page to the LRZ site

Once the site exists: `rsync` this folder's page files to `htdocs/` over SSH — a
one-line script will live in `tools/`. `availability.json` is edited either here and
re-synced, or directly on the server via SFTP; either way it's one file.

## 8. Sources

- LRZ-Benutzungsrichtlinien §4 Abs. 3, 4, 8; §5 Abs. 2 —
  https://www.lrz.de/user_upload/Service-Center/Download-Bereich/LRZ-Benutzungsrichtlinien.pdf
- LRZ-Passwortrichtlinie (20.05.2020), §1 Nr. 5, §3, Verbindliche Anmerkung 2 —
  https://www.lrz.de/fileadmin/Medien/Downloadbereich/Regelwerk/LRZ-Passwortrichtlinie.pdf
- Webhosting beantragen — https://doku.lrz.de/webhosting-website-beantragen-10614696.html
- Umfang des Standard-Webhostings — https://doku.lrz.de/umfang-des-standard-webhostings-10614687.html
- PHP in der Webhosting-Umgebung — https://doku.lrz.de/php-in-der-webhosting-umgebung-343295993.html
- Mailversand aus dem Webhosting — https://doku.lrz.de/mailversand-aus-dem-webhosting-10614686.html
- Vergleich der Postausgangsserver — https://doku.lrz.de/vergleich-der-postausgangsserver-450827392.html
