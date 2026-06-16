# 📦 Project Handover — Haifong Automation Skills & Course
### 海峰棋院 自動化技能・課程・程式 交接文件

> **Purpose of this document:** a single entry point that packs everything produced
> in this session so you can stand up a **Cowork project** and hand it to
> 海峰棋院 (Haifong Go Academy). It explains *what exists*, *how the pieces fit*,
> *how to start*, and *what to do next*.

---

## 1. What this project is

A small, practical toolkit + curriculum that teaches **non-technical academy staff
and students** to automate everyday operations — student rosters, **tournament
pairing/results (賽事配對與成績)**, feedback surveys, and family notifications —
using an **AI assistant + ready-made prompts + reusable code modules**.

It has three layers that work together:

```
   📘 Skills Book (reference)   →   🧩 Code modules (do the work)   →   🎓 24h Course (teach it)
   SKILLS_BOOK_HAIFONG.md           skills/ + email_notification.py     TEACHING_GUIDE_HAIFONG.md
```

---

## 2. Deliverables (the handover package)

| # | File | What it is | Language |
|---|------|-----------|----------|
| 1 | **`SKILLS_BOOK_HAIFONG.md`** | Tailored catalog of ~28 automation **skills + copy-paste prompts**, sorted by function, mapped to academy operations | 繁體中文 |
| 2 | **`skills/`** package | **Working, tested code** for the skills (see §4) | code + EN docs |
| 3 | **`TEACHING_GUIDE_HAIFONG.md`** | **24-hour course** (24×1h, 6 units) for non-tech students: lesson-by-lesson plan, hands-on steps, homework, capstone rubric | 繁體中文 |
| – | `SKILLS_BOOK.md` | The original **generic** English skills book (source material; keep for reference) | English |
| – | `requirements.txt`, `.gitignore` | Dependencies + ignore rules (secrets, caches, outputs) | – |

> The generic English `SKILLS_BOOK.md` is the parent of the Haifong version. Hand
> the **Haifong** files to the academy; keep the generic one as a template for
> tailoring to other organizations later.

---

## 3. Repository map

```
prod_automations/
├── HANDOVER.md                 ← you are here (start here)
├── SKILLS_BOOK_HAIFONG.md      ← 技能手冊 (reference for staff)
├── TEACHING_GUIDE_HAIFONG.md   ← 24h 教案 (for the instructor)
├── SKILLS_BOOK.md              ← generic English source book
│
├── skills/                     ← reusable code modules
│   ├── __init__.py             ← lazy imports (no pandas needed for light modules)
│   ├── report_puller.py        ← Skills 1.1/1.2/1.4  pull reports, date windows, batches
│   ├── transform.py            ← Skills 2.1–2.5       rename/filter/date/derive/skip-rows
│   ├── sftp_transfer.py        ← Skills 3.1–3.3       SFTP upload, dated writes, temp staging
│   ├── polling_export.py       ← Skills 1.3/5.2       async create→poll→download export
│   ├── retry.py                ← Skill 6.4            network retry w/ exponential backoff
│   └── tournament.py           ← Skills 4.2/4.3       Go pairing & standings (HAS SELF-TEST)
│
├── email_notification.py       ← Skills 5.x/6.x       SMTP send w/ attachments
├── run_automation.bat          ← Skill 7.1            generic runner + logging
├── config.env.example          ← Skill 8.x            env-var/secret template
└── requirements.txt            ← pandas, numpy, requests, paramiko
```

---

## 4. The `skills/` modules (what runs)

| Module | Skills | Key functions |
|--------|--------|--------------|
| `report_puller.py` | 1.1, 1.2, 1.4 | `pull_report`, `date_window`, `build_report_url`, `pull_batch` |
| `transform.py` | 2.1–2.5 | `standardize_columns`, `keep_columns`, `format_dates`, `add_stamp`, `parse_skip_rows` |
| `sftp_transfer.py` | 3.1–3.3 | `sftp_upload`, `write_dated_csv`, `staged_file` |
| `polling_export.py` | 1.3, 5.2 | `export_responses` (create→poll→download→unzip) |
| `retry.py` | 6.4 | `retry` (decorator), `with_retry` |
| `tournament.py` | 4.2, 4.3 | `pair_round` (single-elim / swiss / round-robin), `update_standings`, `handicap` |

**`tournament.py` is the academy's centerpiece** and is fully runnable with a
built-in self-test (no external data or pandas needed):

```bash
python skills/tournament.py     # prints demos + "All self-tests passed ✔"
```

It covers: single-elimination (海峰盃 style) with seeding & byes, Swiss (avoids
rematches, auto-bye), round-robin, **handicap/讓子** from dan-kyu rank (EN + 中文),
and standings with **SOS (對手分)** tiebreak.

---

## 5. Quick start (for whoever runs it)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create your private config from the template (NEVER commit the filled-in file)
cp config.env.example config.env      # then edit with real values

# 3. Verify the tournament engine works
python skills/tournament.py

# 4. Run a job via the generic runner (Windows)
run_automation.bat <script_name.py>
```

> **Safety:** `config.env`, caches, and `output/` `logs/` are already git-ignored.
> Use **de-identified practice data** when teaching — never real student/parent PII.

---

## 6. How to teach it

1. Open **`TEACHING_GUIDE_HAIFONG.md`** — it's the instructor's script.
2. Course = **6 units / 24 one-hour lessons** (also packable as 12×2h or a 4-day camp).
3. Each lesson has: 目標 (goal) · 核心觀念 (concept) · 動手做 (hands-on steps) ·
   檢核 (check) · 作業 (homework).
4. Students reference **`SKILLS_BOOK_HAIFONG.md`** for the prompts; they run the
   **`skills/`** modules. Unit 4 (賽事) uses `tournament.py` directly.
5. Finish with a **capstone** (rubric included): automate one real academy workflow
   end-to-end (e.g. 賽事一條龍: registration → pairing → results → publish → notify).

---

## 7. Status

- **Branch:** `claude/skills-book-prompts-aarckz`
- **Pull Request:** [#1 — Add Skills Book…](https://github.com/chelsea-homann/prod_automations/pull/1) (ready for review)
- **CI:** none configured on this repo (nothing to gate merge).
- **Verified:** `skills/tournament.py` self-test passes; all modules pass syntax checks.
  Full runtime of pandas/paramiko modules wasn't exercisable in the build env
  (those deps aren't installed there) — they're pinned in `requirements.txt`.

### Session commit history (this branch)
```
9b3a900 Add 24-hour automation teaching guide for non-tech students (Haifong)
24630e5 Add .gitignore for Python caches, secrets, and outputs
1624fed Add tournament.py: Go pairing & standings (Skills 4.2/4.3) + lazy package imports
384932e Add Haifong Go Academy tailored Skills Book (Traditional Chinese)
e49a391 Add reusable skills/ package and requirements.txt
a4bd19b Add Skills Book: reusable automation skills & prompts sorted by function
```

---

## 8. Suggested Cowork project setup

**Recommended project structure / boards:**

- **Reference** — `SKILLS_BOOK_HAIFONG.md` (pin as the team wiki/handbook).
- **Course delivery** — `TEACHING_GUIDE_HAIFONG.md`; create one task per Unit (1–6),
  optionally one sub-task per Lesson, to track teaching progress.
- **Codebase** — link this repo / PR #1; the `skills/` folder is the shippable code.
- **Backlog** — see §9.

---

## 9. Next-steps backlog (proposed)

| Priority | Item | Why |
|----------|------|-----|
| ★ High | `examples/run_haifong_cup.py` demo script (roster CSV → 編排表 + standings CSV) | Gives Lesson 13–15 a concrete, runnable artifact |
| ★ High | Confirm academy's real systems (student DB, survey tool, LINE vs email) | Lets us replace placeholder URLs/prompts with real ones |
| Med | `tests/` for `tournament.py` (proper pytest file) | Confidence as rules get customized |
| Med | Draft `tournament.py` dan-kyu **promotion rules** (Skill 4.4) per academy policy | Currently a prompt; make it concrete code |
| Med | LINE Notify module (Skill 6.3 extension) | Parents typically use LINE over email |
| Low | Translate `TEACHING_GUIDE` excerpts to bilingual for mixed cohorts | Wider audience |

---

## 10. Open questions for the academy

1. What is the **student-management / registration system** (so we can wire real
   report URLs into Skill 1.x)?
2. Which **survey tool** do you use (Skill 5.x)?
3. **LINE or email** for family notifications (Skill 6.x)?
4. What are the **dan/kyu promotion rules** (Skill 4.4)?
5. Preferred **cohort**: staff/admin, coaches, or students — to tune Unit 1 depth?

---

*Everything here lives on branch `claude/skills-book-prompts-aarckz` / PR #1.*
*To tailor this toolkit for another organization, start from the generic
`SKILLS_BOOK.md` and repeat the Haifong tailoring pattern.*
