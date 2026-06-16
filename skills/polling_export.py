"""
Skill 1.3 / 4.2 - Asynchronous polling-export client
====================================================
A reusable client for the common "create -> poll -> download -> unzip" export
pattern used by survey/analytics APIs (e.g. Qualtrics v3 response export).

Network calls are wrapped with exponential-backoff retry (Skill 6.4).

Usage
-----
    from skills.polling_export import export_responses

    zf, names = export_responses(
        base_url=f"https://{dc}.az1.example.com/API/v3/surveys/{sid}/export-responses/",
        api_token=token, file_format="csv",
    )
"""

import io
import re
import json
import time
import zipfile

import requests

from .retry import retry


@retry(max_attempts=4, base_delay=2.0)
def _post(url, **kwargs):
    r = requests.post(url, **kwargs)
    r.raise_for_status()
    return r


@retry(max_attempts=4, base_delay=2.0)
def _get(url, **kwargs):
    r = requests.get(url, **kwargs)
    r.raise_for_status()
    return r


def export_responses(base_url, api_token, file_format="csv", use_labels=True,
                     proxies=None, survey_id=None, poll_interval=0.0):
    """
    Run a create -> poll -> download -> unzip export and return (ZipFile, names).

    Parameters
    ----------
    base_url : str        The export-responses endpoint (trailing slash).
    api_token : str       Value for the x-api-token header.
    file_format : str     One of csv, tsv, spss.
    use_labels : bool     Request human-readable labels.
    proxies : dict|None   Optional requests proxies (Skill 7.3).
    survey_id : str|None  If given, validated against ^SV_.
    poll_interval : float Seconds to sleep between progress polls.
    """
    if file_format not in ("csv", "tsv", "spss"):
        raise ValueError(f"file_format must be csv, tsv, or spss (got '{file_format}')")
    if survey_id is not None and not re.match(r"^SV_", survey_id):
        raise ValueError(f"survey_id must match ^SV_ (got '{survey_id}')")

    headers = {"content-type": "application/json", "x-api-token": api_token}

    # Step 1: create export
    payload = json.dumps({"format": file_format, "useLabels": use_labels})
    progress_id = _post(base_url, data=payload, headers=headers,
                        proxies=proxies).json()["result"]["progressId"]
    print(f"Export initiated (progressId: {progress_id})")

    # Step 2: poll until complete/failed
    status, result = "inProgress", None
    while status not in ("complete", "failed"):
        result = _get(base_url + progress_id, headers=headers,
                      proxies=proxies).json()["result"]
        status = result["status"]
        print(f"  Progress: {result['percentComplete']}% ({status})")
        if poll_interval and status not in ("complete", "failed"):
            time.sleep(poll_interval)
    if status == "failed":
        raise RuntimeError("Export failed")

    # Step 3: download finished file
    file_id = result["fileId"]
    download = _get(base_url + file_id + "/file", headers=headers,
                    proxies=proxies, stream=True)

    # Step 4: unzip in memory
    zf = zipfile.ZipFile(io.BytesIO(download.content))
    names = zf.namelist()
    print(f"Extracted files: {names}")
    return zf, names
