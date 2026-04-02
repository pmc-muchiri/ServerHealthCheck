from __future__ import annotations

import subprocess

from .app_logging import get_logger


def _read_trusted_hosts_raw() -> str:
    logger = get_logger()
    command = "(Get-Item WSMan:\\localhost\\Client\\TrustedHosts -ErrorAction Stop).Value"
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        logger.error("TrustedHosts lookup failed with code=%s", completed.returncode)
        raise RuntimeError((completed.stderr or completed.stdout or "Unable to read WinRM TrustedHosts").strip())
    return completed.stdout.strip()


def get_trusted_hosts() -> list[str]:
    raw = _read_trusted_hosts_raw()
    if not raw:
        return []
    return [entry.strip() for entry in raw.split(",") if entry.strip()]


def is_target_trusted(target: str) -> tuple[bool, list[str]]:
    normalized = (target or "").strip().lower()
    entries = get_trusted_hosts()
    lowered_entries = [entry.lower() for entry in entries]
    if "*" in lowered_entries:
        return True, entries
    if normalized in lowered_entries:
        return True, entries
    return False, entries
