from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import DatabaseDetail, Metric, RequirementRow, ServiceStatus, Snapshot


def _escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in str(value))
    compact = "-".join(part for part in cleaned.split("-") if part)
    return compact or "server"


def _metric_rows(metrics: list[Metric]) -> str:
    rows: list[str] = []
    for metric in metrics:
        status = "WARNING" if metric.tone == "amber" else "OK"
        klass = "warning" if metric.tone == "amber" else "ok"
        rows.append(
            f"<tr><td>{_escape(metric.label)}</td><td>{_escape(metric.display_value)}</td>"
            f"<td>{_escape(metric.max_label)}</td><td>{metric.progress}%</td><td class='{klass}'>{status}</td></tr>"
        )
    return "".join(rows)


def _service_rows(services: list[ServiceStatus]) -> str:
    if not services:
        return "<tr><td>No inspected services available.</td><td>-</td><td>-</td></tr>"
    return "".join(
        f"<tr><td>{_escape(service.name)}</td><td>{_escape(service.status)}</td><td>{_escape(service.uptime)}</td></tr>"
        for service in services
    )


def _requirement_rows(requirements: list[RequirementRow]) -> str:
    return "".join(
        f"<tr><td>{_escape(row.component)}</td><td>{_escape(row.required)}</td>"
        f"<td>{_escape(row.actual)}</td><td>{'PASS' if row.passed else 'CHECK'}</td></tr>"
        for row in requirements
    )


def _database_rows(database_details: list[DatabaseDetail]) -> str:
    filtered_details = [detail for detail in database_details if detail.label != "Installed Software"]
    if not filtered_details:
        return "<tr><td>No inspected database details available.</td><td>Unavailable</td></tr>"
    return "".join(
        f"<tr><td>{_escape(detail.label)}</td><td>{_escape(detail.value)}</td></tr>"
        for detail in filtered_details
    )


def _software_rows(installed_software: list[str]) -> str:
    if not installed_software:
        return "<tr><td>No installed software inventory available.</td></tr>"
    return "".join(
        f"<tr><td>{_escape(software)}</td></tr>"
        for software in installed_software
    )


def build_report_section(snapshot: Snapshot, metrics: list[Metric], requirements: list[RequirementRow]) -> str:
    report_status = "Healthy" if all(service.status == "Running" for service in snapshot.service_statuses) else "Attention Needed"
    summary_requirements = f"{sum(1 for item in requirements if item.passed)}/{len(requirements)} passed" if requirements else "0/0 passed"
    return f"""
  <h1>System Housekeeping Report</h1>
  <div class="sub mono">Server: {_escape(snapshot.computer_name)} • IP: {_escape(snapshot.primary_ip)} • Generated: {_escape(snapshot.checked_at)}</div>
  <div class="summary">
    <div class="card"><div class="label">Status</div><div class="value ok">{_escape(report_status)}</div></div>
    <div class="card"><div class="label">Uptime</div><div class="value mono">{_escape(snapshot.uptime_display)}</div></div>
    <div class="card"><div class="label">Requirements</div><div class="value">{_escape(summary_requirements)}</div></div>
  </div>
  <div class="section">
    <h2>Resource Utilization</h2>
    <table><thead><tr><th>Metric</th><th>Current</th><th>Total</th><th>Usage</th><th>Status</th></tr></thead><tbody>{_metric_rows(metrics)}</tbody></table>
  </div>
  <div class="section">
    <h2>Services</h2>
    <table><thead><tr><th>Service</th><th>Status</th><th>Uptime</th></tr></thead><tbody>{_service_rows(snapshot.service_statuses)}</tbody></table>
  </div>
  <div class="section">
    <h2>System Requirements Check</h2>
    <table><thead><tr><th>Component</th><th>Required</th><th>Actual</th><th>Status</th></tr></thead><tbody>{_requirement_rows(requirements)}</tbody></table>
  </div>
  <div class="section">
    <h2>Database Configuration</h2>
    <table><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{_database_rows(snapshot.database_details)}</tbody></table>
  </div>
  <div class="section">
    <h2>Installed Software</h2>
    <table class="software-table"><thead><tr><th>Software</th></tr></thead><tbody>{_software_rows(snapshot.installed_software)}</tbody></table>
  </div>
"""


def build_report(snapshot: Snapshot, metrics: list[Metric], requirements: list[RequirementRow]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>System Housekeeping Report</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 24px; color: #0f172a; }}
    h1, h2 {{ margin: 0; }}
    .sub {{ color: #64748b; margin-top: 6px; font-size: 13px; }}
    .summary {{ display: flex; gap: 16px; margin: 24px 0; }}
    .card {{ border: 1px solid #d8e1ec; border-radius: 12px; padding: 12px 16px; min-width: 120px; }}
    .label {{ font-size: 11px; text-transform: uppercase; color: #64748b; margin-bottom: 6px; }}
    .value {{ font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid #d8e1ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ color: #516b93; font-size: 12px; text-transform: uppercase; }}
    .ok {{ color: #16a34a; font-weight: 700; }}
    .warning {{ color: #f59e0b; font-weight: 700; }}
    .section {{ margin-top: 28px; }}
    .mono {{ font-family: Consolas, "Courier New", monospace; }}
    .software-table td {{ word-break: break-word; }}
  </style>
</head>
<body>
{build_report_section(snapshot, metrics, requirements)}
</body>
</html>"""


def build_combined_report(report_sections: list[str]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>System Housekeeping Reports</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 24px; color: #0f172a; background: #f8fafc; }}
    .server-report {{ background: #ffffff; border: 1px solid #d8e1ec; border-radius: 16px; padding: 20px; margin-bottom: 24px; }}
  </style>
</head>
<body>
  {''.join(f"<section class='server-report'>{section}</section>" for section in report_sections)}
</body>
</html>"""


def export_report(snapshot: Snapshot, metrics: list[Metric], requirements: list[RequirementRow], directory: Path) -> Path:
    report_date = datetime.now().strftime("%Y-%m-%d")
    server_name = snapshot.computer_name if snapshot.computer_name != "Unavailable" else snapshot.primary_ip
    filename = f"housekeeping-report-{_slugify(server_name)}-{report_date}.html"
    output_path = directory / filename
    output_path.write_text(build_report(snapshot, metrics, requirements), encoding="utf-8")
    return output_path


def export_combined_report(report_sections: list[str], directory: Path, report_name: str = "all-servers") -> Path:
    report_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"housekeeping-report-{report_name}-{report_date}.html"
    output_path = directory / filename
    output_path.write_text(build_combined_report(report_sections), encoding="utf-8")
    return output_path
