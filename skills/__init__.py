"""
Reusable Automation Skills
==========================
Drop-in building blocks distilled from the prod_automations toolkit and
documented in SKILLS_BOOK.md (and the Haifong-tailored SKILLS_BOOK_HAIFONG.md).
Each module is independent so you can compose them into a pipeline
(extract -> transform -> deliver -> notify).

Modules
-------
retry           - Skill 6.4: retry network calls with exponential backoff
report_puller   - Skills 1.1, 1.2, 1.4: pull RaaS/HTTP reports, date windows, batches
polling_export  - Skill 1.3 / 4.2: async create->poll->download export client
transform       - Skills 2.1-2.5: rename, filter, date-format, derive, skip rows
sftp_transfer   - Skills 3.1-3.3: SFTP upload, dated output writes, temp staging
tournament      - Skills 4.2/4.3: Go pairing (single-elim/swiss/round-robin) & standings

Email notifications (Skill 5.x) live in the top-level email_notification module.

Submodules are imported lazily (PEP 562) so importing one that has no heavy
dependency (e.g. ``skills.tournament``, ``skills.retry``) never forces pandas
or paramiko to be installed.
"""

import importlib

__all__ = ["retry", "report_puller", "polling_export", "transform",
           "sftp_transfer", "tournament"]


def __getattr__(name):
    if name in __all__:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
