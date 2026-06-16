# 📘 The Skills Book

### A catalog of reusable automation skills & prompts for People-Analytics / HR Operations work

This book turns the patterns living inside `prod_automations` into **skills** —
self-contained capabilities you can drop into your own work — each paired with a
**ready-to-use prompt** you can hand to an AI coding assistant (e.g. Claude) to
generate, adapt, or extend that capability.

Skills are **sorted by function** so you can jump straight to the category you need:

| # | Function | What it covers | Skills |
|---|----------|----------------|--------|
| 1 | [Data Extraction & Ingestion](#1-data-extraction--ingestion) | Pulling data out of source systems | 1.1 – 1.4 |
| 2 | [Data Transformation & Cleaning](#2-data-transformation--cleaning) | Reshaping data for downstream use | 2.1 – 2.5 |
| 3 | [File Transfer & Delivery](#3-file-transfer--delivery) | Moving files to where they're needed | 3.1 – 3.3 |
| 4 | [Survey Operations](#4-survey-operations) | Driving survey platforms end-to-end | 4.1 – 4.3 |
| 5 | [Notifications & Communication](#5-notifications--communication) | Telling humans what happened | 5.1 – 5.3 |
| 6 | [Orchestration & Scheduling](#6-orchestration--scheduling) | Running jobs reliably and on time | 6.1 – 6.4 |
| 7 | [Configuration & Security](#7-configuration--security) | Secrets, environments, and safety | 7.1 – 7.4 |

> **How to use a prompt:** copy the prompt block, fill in the `<angle-bracket>`
> placeholders with your specifics, and paste it into your assistant. Each prompt
> is written to produce production-ready, configurable Python (matching the style
> already used in this repo: env-var config, no hard-coded secrets, email on
> failure).

---

## 1. Data Extraction & Ingestion

> *Source of truth → your hands.* Skills for getting data out of APIs, report
> engines, and databases into a clean DataFrame.

### 1.1 Pull a report from an HTTP/RaaS endpoint
**What it does:** Authenticates to a report-as-a-service URL (e.g. Workday RaaS),
downloads a CSV, and returns it as a pandas DataFrame.
**Reference:** `pull_HRIS_report()` in `hris_monthly_pull.py`, `saas_survey_automation.py`

```text
Write a Python function `pull_report(url, username, password)` that:
- Uses a requests.Session with HTTP Basic Auth
- Downloads a CSV from <REPORT_SYSTEM> (a RaaS-style endpoint)
- Calls raise_for_status() and decodes UTF-8
- Returns a pandas DataFrame via io.StringIO
Read the URL and credentials from environment variables, never hard-code them.
```

### 1.2 Parameterize a report by date range
**What it does:** Injects `{start_dt}` / `{end_dt}` placeholders into a report URL
template so the same job can run for any rolling window.
**Reference:** `build_report_url()` + `LOOKBACK_DAYS`/`LOOKFORWARD_DAYS` logic

```text
Add a date-windowing helper to my report puller. Given a base URL template
containing {start_dt} and {end_dt}, compute start = today - LOOKBACK_DAYS and
end = today + LOOKFORWARD_DAYS (both env-configurable, format YYYY-MM-DD) and
format them into the URL. Default lookback=<4>, lookforward=<0>.
```

### 1.3 Export data from a polling API (async job pattern)
**What it does:** Kicks off a server-side export, polls a progress endpoint until
`complete`/`failed`, then downloads the resulting file (often a zip).
**Reference:** `export_survey()` in `saas_survey_export.py`

```text
Implement a Python client for an asynchronous export API that follows the
create → poll → download pattern:
1. POST to start the export and capture a progressId
2. GET the progress endpoint in a loop, printing percentComplete, until status
   is "complete" or "failed" (raise on failure)
3. Download the finished file by fileId and unzip it in memory with zipfile
Validate inputs up front (e.g. survey id must match ^SV_, format in csv/tsv/spss).
Auth via an x-api-token header read from an env var. Support optional HTTP/HTTPS proxies.
```

### 1.4 Pull a configurable batch of reports
**What it does:** Iterates over a JSON-defined list of `{name, url, output}` report
configs and pulls each one — so adding a report is config, not code.
**Reference:** candidate-reports loop in `hris_monthly_pull.py`

```text
Refactor my multi-report job so the set of reports comes from a single env var
holding a JSON array like
[{"name":"Program A","url":"https://...","output":"a.csv"}].
Loop over the array, pull each report, apply column renames, and save to OUTPUT_DIR.
Skip any report whose URL env var is empty rather than failing.
```

---

## 2. Data Transformation & Cleaning

> *Raw → ready.* Skills for standardizing, filtering, and enriching tabular data
> before it's delivered or loaded.

### 2.1 Standardize column names (system → human-readable)
**What it does:** Renames source columns (e.g. underscore/system names) to clean,
report-friendly labels — but only for columns that actually exist.
**Reference:** `*_RENAMES` dicts applied in `hris_monthly_pull.py`

```text
Add column standardization to my DataFrame pipeline. Keep a rename map at the top
of the module. Before renaming, filter the map to keys that exist in the frame
(`{k:v for k,v in RENAMES.items() if k in df.columns}`) so missing columns never
raise. Make the map easy to extend.
```

### 2.2 Select / filter columns to keep
**What it does:** Reduces a wide export to an approved column subset, ignoring any
requested columns that aren't present.
**Reference:** `COLUMNS_TO_KEEP` logic in `saas_survey_export.py`

```text
Add optional column filtering controlled by an env var COLUMNS_TO_KEEP (JSON list).
If set, keep only those columns that are present in the frame (preserve order);
if unset, keep everything. Print how many columns were kept.
```

### 2.3 Normalize date formatting
**What it does:** Detects date-like columns and reformats them to a consistent
display format (e.g. `MM/DD/YYYY`), tolerating unparseable values.
**Reference:** date-formatting loop in `saas_survey_export.py`

```text
Write a step that scans DataFrame columns whose name contains <"Date"> and
reformats them with pd.to_datetime(...).dt.strftime('%m/%d/%Y'), wrapped in
try/except so non-date columns are silently skipped.
```

### 2.4 Add derived / audit columns
**What it does:** Appends computed columns such as a run/launch date stamp, and
drops superseded source columns.
**Reference:** `SAAS Survey Launch Date` handling in `saas_survey_automation.py`

```text
After loading the report, add a column "<Launch Date>" set to today's date
(format MM-DD-YYYY), and drop the original "<Survey_Launch_Date>" column if it
exists. Make the column name and date format constants at the top of the file.
```

### 2.5 Skip junk header/metadata rows on read
**What it does:** Handles exports that carry extra header/description rows by
skipping specific row indices at read time.
**Reference:** `SKIP_ROWS` logic in `saas_survey_export.py`

```text
Support an env var SKIP_ROWS (comma-separated indices, e.g. "0,2"). When set,
read the CSV with skiprows=lambda x: x in those indices and header=0; otherwise
read normally. This handles platform exports that include extra metadata rows.
```

---

## 3. File Transfer & Delivery

> *Here → there.* Skills for landing files where downstream systems and people
> expect them.

### 3.1 Upload a file over SFTP
**What it does:** Connects to an SFTP server with paramiko, removes any stale copy,
and uploads the new file to a remote directory.
**Reference:** `sftp_upload()` in `saas_survey_automation.py`

```text
Write `sftp_upload(host, user, password, remote_dir, local_path, remote_filename)`
using paramiko: open an SSH client (AutoAddPolicy), chdir to remote_dir, delete
the existing remote file if present (ignore FileNotFoundError), put the local
file, then close sftp and ssh. Read all connection details from env vars.
```

### 3.2 Write a timestamped CSV to a shared/output directory
**What it does:** Ensures the output directory exists and writes a dated filename so
historical runs don't overwrite each other.
**Reference:** output-path logic in `saas_survey_export.py`, `hris_monthly_pull.py`

```text
Add an output writer that os.makedirs(OUTPUT_DIR, exist_ok=True), builds a
filename like "<prefix>_<MM-YYYY>.csv", and writes df.to_csv(path, index=False,
na_rep=''). Print the final path.
```

### 3.3 Stage to a temp file, then clean up
**What it does:** Writes to a `tempfile`-managed path for transfer, then removes the
local copy after a successful handoff.
**Reference:** `tempfile.mkdtemp()` + `os.remove()` in `saas_survey_automation.py`

```text
Refactor my transfer job to stage the CSV in a tempfile.mkdtemp() directory,
upload it, and only os.remove() the local copy after the upload succeeds. On
failure, leave the file in place and attach it to the failure email.
```

---

## 4. Survey Operations

> *End-to-end survey plumbing.* Skills that feed participants in and pull responses
> back out of survey platforms (Qualtrics-style APIs).

### 4.1 Build & upload a participant feed
**What it does:** Pulls an eligible-population report, reshapes it for the survey
platform's import schema, and SFTPs it to the platform's inbound directory.
**Reference:** `saas_survey_automation.py` (full pipeline)

```text
Build an end-to-end "participant feed" automation:
1. Pull an eligibility report from <HRIS> for the last LOOKBACK_DAYS
2. Rename columns to the survey platform's expected schema; add a launch-date column
3. Write a temp CSV and SFTP it to the platform's inbound directory
4. Email success; on any failure email the error (attach the CSV on transfer failures)
Support a regional variant via a different report URL / lookforward window.
```

### 4.2 Export survey responses
**What it does:** Uses the platform's response-export API (create/poll/download/unzip)
to retrieve completed responses as a CSV.
**Reference:** `export_survey()` + `main()` in `saas_survey_export.py`

```text
Use Skill 1.3's polling-export client to export survey responses with useLabels=true,
unzip the result, read the first .csv into a DataFrame, and hand it to my cleaning
pipeline (Skills 2.2–2.5). Read survey id, datacenter, and API token from env vars.
```

### 4.3 Deliver the response export to stakeholders
**What it does:** Saves the cleaned response file and emails it to a distribution
list as an attachment.
**Reference:** email-with-attachment step in `saas_survey_export.py`

```text
After exporting and cleaning survey responses, save a dated CSV and, if
EMAIL_RECIPIENTS is set, email it as an attachment with subject
"<MM-YYYY> Survey Data Export". Skip the email gracefully if no recipients.
```

---

## 5. Notifications & Communication

> *Close the loop with humans.* Skills for status alerts so jobs never fail silently.

### 5.1 Send an SMTP email (with optional attachment)
**What it does:** A reusable `send_email()` helper supporting plain-text bodies and
optional file attachments via `MIMEMultipart`.
**Reference:** `email_notification.py`

```text
Write a reusable send_email(sender, recipients, subject, body, smtp_host=None,
smtp_port=None, attachment_name=None, attachment_path=None) helper using smtplib
and email.mime. Fall back to SMTP_HOST/SMTP_PORT env vars (default port 25).
If an attachment is requested, base64-encode it as a MIMEBase octet-stream and
raise FileNotFoundError if the path is missing.
```

### 5.2 Success / failure job alerts
**What it does:** Wraps each stage in try/except and emails a clear success or
failure message (including the exception text) to the team.
**Reference:** the `try/except → send_email` pattern across the automations

```text
Wrap each stage of my job in try/except. On success send a "<Job> Completed"
email; on failure send a "<Job> Failed" email containing the stage name and the
exception, then exit non-zero. Reuse my send_email helper.
```

### 5.3 Attach the artifact to failure alerts
**What it does:** When a delivery step fails, attaches the generated file to the
alert so an operator can act on it immediately.
**Reference:** SFTP-failure branch in `saas_survey_automation.py`

```text
On transfer failures specifically, attach the file that was being delivered to
the failure email (attachment_name + attachment_path) so an operator can deliver
it manually without re-running the job.
```

---

## 6. Orchestration & Scheduling

> *Run it reliably, run it on time.* Skills for wrapping scripts into dependable jobs.

### 6.1 Generic script runner with logging
**What it does:** A wrapper that activates the right environment, runs any script by
name, and tees stdout/stderr to a per-script log file with success/fail status.
**Reference:** `run_automation.bat`

```text
Write a generic runner (<bat/shell>) that: activates the <conda> env named in an
env var, takes a script filename as $1, runs it with python, redirects stdout+stderr
to logs/<script>_log.txt, and prints [SUCCESS]/[FAILED] based on the exit code.
```

### 6.2 Schedule a recurring job
**What it does:** Registers the runner with the OS scheduler (Task Scheduler / cron)
on a daily or monthly cadence.
**Reference:** intended usage of `run_automation.bat`

```text
Give me the <Windows Task Scheduler / cron> configuration to run
`run_automation.bat <script.py>` <daily at 6am / monthly on the 1st>. Include the
exact command line, working directory, and how to capture logs.
```

### 6.3 Exit-code discipline
**What it does:** Ensures scripts return non-zero on failure so the scheduler and
runner can detect and react to problems.
**Reference:** `sys.exit(1)` on failure branches

```text
Audit my script for exit-code correctness: every unrecoverable failure path must
sys.exit(1) (after notifying), and the happy path must exit 0. Point out any
except block that swallows an error without exiting.
```

### 6.4 Network retry with backoff
**What it does:** Wraps flaky network calls (report pulls, SFTP, SMTP) in retries
with exponential backoff so transient blips don't fail the run.
**Reference:** recommended hardening for `requests`/`paramiko` calls

```text
Add a retry decorator/helper with exponential backoff (e.g. 2s, 4s, 8s, 16s; max
<4> attempts) and apply it to network operations — report download, SFTP upload,
and SMTP send. Only retry on transient/connection errors, not on auth/4xx errors.
```

---

## 7. Configuration & Security

> *Safe by construction.* Skills for handling secrets, environments, and corporate
> network realities.

### 7.1 Externalize all config to environment variables
**What it does:** Moves every credential, URL, and tunable into env vars documented
in a committed `config.env.example` (never the filled-in file).
**Reference:** `config.env.example`

```text
Extract every hard-coded value in my script (credentials, URLs, hosts, output
paths, date windows) into os.environ reads with sensible defaults via .get().
Generate a config.env.example documenting each variable with a comment, and add
config.env to .gitignore. Never commit real secrets.
```

### 7.2 Required vs optional variables
**What it does:** Fails fast with a clear error when a *required* secret is missing,
while allowing optional settings to default.
**Reference:** `os.environ['X']` (required) vs `os.environ.get('X', default)` (optional)

```text
Classify my env vars into required (use os.environ['X'] so a missing one raises
immediately at startup) and optional (os.environ.get('X', default)). List which
is which at the top of the file.
```

### 7.3 Corporate proxy support
**What it does:** Threads optional HTTP/HTTPS proxy settings through outbound
requests for locked-down networks.
**Reference:** `PROXY_HTTP` / `PROXY_HTTPS` handling in `saas_survey_export.py`

```text
Add optional proxy support: if PROXY_HTTP or PROXY_HTTPS env vars are set, build a
proxies dict and pass it to every requests call; otherwise pass proxies=None.
```

### 7.4 Secret-handling hygiene
**What it does:** Keeps secrets out of source, logs, and version control; documents
the load mechanism per platform.
**Reference:** header guidance in `config.env.example`

```text
Review my repo for secret hygiene: ensure no credentials appear in source, logs,
or committed files; confirm config.env is gitignored; and document how to load
secrets on <Windows .bat SET wrapper / Linux source config.env>. Flag any place a
secret could be printed to a log.
```

---

## Appendix A — Skill-to-source map

| Skill | Primary source file(s) |
|-------|-------------------------|
| 1.1, 1.2, 1.4, 2.1 | `hris_monthly_pull.py` |
| 1.2, 2.4, 3.1, 3.3, 4.1, 5.3 | `saas_survey_automation.py` |
| 1.3, 2.2, 2.3, 2.5, 4.2, 4.3, 7.3 | `saas_survey_export.py` |
| 5.1, 5.2 | `email_notification.py` |
| 6.1, 6.2, 6.3 | `run_automation.bat` |
| 7.1, 7.2, 7.4 | `config.env.example` |

## Appendix B — Composing skills into a pipeline

A typical automation chains skills across functions. Example — **a daily survey
participant feed**:

```
1.2 date window → 1.1 pull report → 2.1 rename cols → 2.4 add launch date
   → 3.3 stage temp file → 3.1 SFTP upload → 3.3 cleanup → 5.2 success/failure alert
```

…and **a monthly response export**:

```
1.3 polling export → 2.5 skip junk rows → 2.2 keep columns → 2.3 format dates
   → 3.2 write dated CSV → 4.3 email to stakeholders
```

Mix and match: each numbered skill is independent, so you can swap a source
(Skill 1.x), change the transform (Skill 2.x), or redirect the delivery (Skill 3.x)
without touching the rest.

---

*Generated for the `prod_automations` toolkit. Extend this book by adding a new
numbered skill under the matching function, with a one-line description, a source
reference, and a copy-paste prompt.*
