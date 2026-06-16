"""
Skills 3.1-3.3 - File transfer & delivery
=========================================
Land files where downstream systems and people expect them: SFTP upload,
timestamped output writes, and a temp-stage-then-cleanup context manager.

The SFTP upload is wrapped with exponential-backoff retry (Skill 6.4).

Usage
-----
    from skills.sftp_transfer import sftp_upload, write_dated_csv, staged_file

    with staged_file("feed.csv") as local_path:
        df.to_csv(local_path, index=False)
        sftp_upload(host, user, pw, remote_dir, local_path, "feed.csv")
"""

import os
import shutil
import tempfile
import contextlib
from datetime import date

import paramiko

from .retry import retry


@retry(max_attempts=4, base_delay=2.0)
def sftp_upload(hostname, username, password, remote_dir, local_path, remote_filename):
    """
    Skill 3.1 - upload a local file to an SFTP server, replacing any stale copy.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        sftp.chdir(remote_dir)
        remote_path = remote_dir.rstrip("/") + "/" + remote_filename
        try:
            sftp.remove(remote_path)
        except FileNotFoundError:
            pass
        sftp.put(local_path, remote_path)
        sftp.close()
    finally:
        ssh.close()


def write_dated_csv(df, output_dir, prefix, fmt="%m-%Y", **to_csv_kwargs):
    """
    Skill 3.2 - ensure ``output_dir`` exists and write ``<prefix>_<date>.csv``.
    Returns the full output path. Extra kwargs pass through to ``df.to_csv``.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{prefix}_{date.today().strftime(fmt)}.csv"
    path = os.path.join(output_dir, filename)
    to_csv_kwargs.setdefault("index", False)
    to_csv_kwargs.setdefault("na_rep", "")
    df.to_csv(path, **to_csv_kwargs)
    print(f"Saved to: {path}")
    return path


@contextlib.contextmanager
def staged_file(filename):
    """
    Skill 3.3 - yield a temp path for ``filename`` and remove the temp dir on exit
    (whether the block succeeds or raises), so local copies never linger.
    """
    tmp_dir = tempfile.mkdtemp()
    try:
        yield os.path.join(tmp_dir, filename)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
