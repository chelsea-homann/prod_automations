"""
Skills 1.1, 1.2, 1.4 - Report extraction & ingestion
====================================================
Pull CSV reports from a report-as-a-service (RaaS) / HTTP endpoint into pandas
DataFrames, with optional date-window parameterization and configurable batches.

All network calls are wrapped with exponential-backoff retry (Skill 6.4).

Usage
-----
    from skills.report_puller import pull_report, build_report_url, date_window, pull_batch

    start, end = date_window(lookback_days=4)
    url = build_report_url(os.environ["REPORT_URL"], start, end)
    df = pull_report(url, user, password)
"""

import io
import json
from datetime import date, timedelta

import requests
import pandas as pd

from .retry import retry


def date_window(lookback_days=4, lookforward_days=0, fmt="%Y-%m-%d", today=None):
    """
    Skill 1.2 - compute (start_dt, end_dt) strings for a rolling report window.

    start = today - lookback_days, end = today + lookforward_days.
    """
    today = today or date.today()
    start = (today - timedelta(days=lookback_days)).strftime(fmt)
    end = (today + timedelta(days=lookforward_days)).strftime(fmt)
    return start, end


def build_report_url(base_url, start_dt, end_dt):
    """Skill 1.2 - inject {start_dt}/{end_dt} placeholders into a URL template."""
    return base_url.format(start_dt=start_dt, end_dt=end_dt)


@retry(max_attempts=4, base_delay=2.0)
def pull_report(url, username, password, encoding="utf-8"):
    """
    Skill 1.1 - download a CSV from a RaaS/HTTP endpoint and return a DataFrame.

    Uses HTTP Basic Auth and raises on any non-2xx response.
    """
    with requests.Session() as session:
        response = session.get(url, auth=(username, password))
        response.raise_for_status()
        decoded = response.content.decode(encoding)
    return pd.read_csv(io.StringIO(decoded))


def pull_batch(configs, username, password, renames=None):
    """
    Skill 1.4 - pull a configurable batch of reports.

    Parameters
    ----------
    configs : list[dict] | str
        Each item is {"name": ..., "url": ..., "output": ...}. A JSON string is
        also accepted (e.g. read straight from an env var).
    renames : dict, optional
        Column rename map applied to every report (missing columns ignored).

    Returns
    -------
    dict[str, pandas.DataFrame]  keyed by the ``output`` filename.
    """
    if isinstance(configs, str):
        configs = json.loads(configs or "[]")

    results = {}
    for cfg in configs:
        name, url, output = cfg["name"], cfg["url"], cfg["output"]
        if not url:
            print(f"Skipping {name}: empty URL")
            continue
        print(f"Pulling {name} report...")
        df = pull_report(url, username, password)
        if renames:
            existing = {k: v for k, v in renames.items() if k in df.columns}
            df = df.rename(columns=existing)
        results[output] = df
        print(f"  {name}: {len(df)} rows")
    return results
