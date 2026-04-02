from __future__ import annotations

import json
import math
import os
import socket
import subprocess
from datetime import datetime

from .app_logging import get_logger
from .models import DatabaseDetail, Metric, RequirementRow, ServiceStatus, Snapshot, StorageVolume


def _run_powershell_json(command: str) -> dict:
    logger = get_logger()
    logger.info("Running PowerShell inspection command")
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        logger.error("PowerShell inspection command failed with code=%s", completed.returncode)
        raise RuntimeError((completed.stderr or completed.stdout or f"PowerShell exited with code {completed.returncode}").strip())
    output = completed.stdout.strip()
    logger.info("PowerShell inspection command completed successfully")
    return json.loads(output) if output else {}


def _sanitize_ps(value: str) -> str:
    return str(value or "").replace("'", "''")


def _clean_text(value) -> str:
    cleaned = " ".join(str(value or "").split())
    return cleaned or "Unavailable"


def _sql_version_name(version: str) -> str:
    mapping = {
        "160": "SQL Server 2022",
        "150": "SQL Server 2019",
        "140": "SQL Server 2017",
        "130": "SQL Server 2016",
        "120": "SQL Server 2014",
        "110": "SQL Server 2012",
    }
    return mapping.get(str(version), "SQL Server")


def _ensure_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _to_float(value, fallback: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return fallback
    return numeric if math.isfinite(numeric) else fallback


def _round1(value: float) -> float:
    return round(float(value), 1)


def _local_ip() -> str:
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return "127.0.0.1"


def inspect_target(target: str = "") -> Snapshot:
    logger = get_logger()
    normalized = (target or "").strip()
    target_expr = f"'{_sanitize_ps(normalized)}'" if normalized else "$env:COMPUTERNAME"
    checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Collecting inspection payload for target=%s", normalized or "local machine")
    payload = _run_powershell_json(
        f"""
        $ErrorActionPreference = 'Stop'
        $computerName = {target_expr}
        $osInfo = Get-CimInstance Win32_OperatingSystem -ComputerName $computerName -ErrorAction Stop
        $computerSystem = Get-CimInstance Win32_ComputerSystem -ComputerName $computerName -ErrorAction Stop
        $processors = @(Get-CimInstance Win32_Processor -ComputerName $computerName -ErrorAction Stop)
        $cpuInfo = $processors | Measure-Object -Property LoadPercentage -Average
        $logicalCpuCount = ($processors | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
        $pageFileTotal = (Get-CimInstance Win32_PageFileUsage -ComputerName $computerName -ErrorAction Stop | Measure-Object -Property AllocatedBaseSize -Sum).Sum
        $pageFileUsed = (Get-CimInstance Win32_PageFileUsage -ComputerName $computerName -ErrorAction Stop | Measure-Object -Property CurrentUsage -Sum).Sum
        $iisService = Get-Service -ComputerName $computerName -Name W3SVC -ErrorAction SilentlyContinue
        $serviceTargets = @(
          @{{ Key = 'MSSQLSERVER'; Label = 'SQL Server (MSSQLSERVER)' }},
          @{{ Key = 'SQLSERVERAGENT'; Label = 'SQL Server Agent' }},
          @{{ Key = 'SQLBrowser'; Label = 'SQL Server Browser' }},
          @{{ Key = 'MsDtsServer160'; Label = 'SSIS' }},
          @{{ Key = 'ReportServer'; Label = 'SSRS' }},
          @{{ Key = 'W3SVC'; Label = 'IIS (W3SVC)' }}
        )
        $serviceRows = @($serviceTargets | ForEach-Object {{
          $service = Get-CimInstance Win32_Service -ComputerName $computerName -Filter "Name='$($_.Key)'" -ErrorAction SilentlyContinue
          if ($service) {{
            $status = if ($service.State -eq 'Running') {{ 'Running' }} else {{ 'Stopped' }}
            $uptime = '-'
            if ($service.ProcessId -and [int]$service.ProcessId -gt 0) {{
              $process = Get-CimInstance Win32_Process -ComputerName $computerName -Filter "ProcessId=$($service.ProcessId)" -ErrorAction SilentlyContinue
              if ($process -and $process.CreationDate) {{
                try {{
                  $startedAt = [System.Management.ManagementDateTimeConverter]::ToDateTime([string]$process.CreationDate)
                  $serviceAge = (Get-Date) - $startedAt
                  if ($serviceAge.TotalSeconds -ge 0) {{
                    $uptime = "{{0}}d {{1:D2}}h {{2:D2}}m" -f [int]$serviceAge.TotalDays, $serviceAge.Hours, $serviceAge.Minutes
                  }}
                }} catch {{
                  $uptime = '-'
                }}
              }}
            }}
            @{{ name = $_.Label; status = $status; uptime = $uptime }}
          }}
        }})
        $disks = @(Get-CimInstance Win32_LogicalDisk -ComputerName $computerName -Filter "DriveType=3" -ErrorAction Stop | Sort-Object DeviceID | ForEach-Object {{
          $sizeGb = if ($_.Size) {{ [math]::Round($_.Size / 1GB, 1) }} else {{ 0 }}
          $freeGb = if ($_.FreeSpace) {{ [math]::Round($_.FreeSpace / 1GB, 1) }} else {{ 0 }}
          $usedGb = [math]::Round($sizeGb - $freeGb, 1)
          $usedPercent = if ($sizeGb -gt 0) {{ [math]::Round(($usedGb / $sizeGb) * 100, 0) }} else {{ 0 }}
          @{{ name = "Disk ($($_.DeviceID))"; totalGb = $sizeGb; freeGb = $freeGb; usedGb = $usedGb; usedPercent = $usedPercent }}
        }})
        $uptime = (Get-Date) - $osInfo.LastBootUpTime
        $freeMemoryGb = [math]::Round(($osInfo.FreePhysicalMemory * 1KB) / 1GB, 1)
        $totalMemoryGb = [math]::Round($computerSystem.TotalPhysicalMemory / 1GB, 1)
        $usedMemoryGb = [math]::Round($totalMemoryGb - $freeMemoryGb, 1)
        $networkSample = $null
        if ($computerName -eq $env:COMPUTERNAME) {{
          $networkSample = (Get-Counter '\\Network Interface(*)\\Bytes Total/sec').CounterSamples |
            Where-Object {{ $_.InstanceName -notmatch 'Loopback|isatap|Teredo' }} |
            Measure-Object -Property CookedValue -Sum
        }}
        $networkMbps = if ($networkSample -and $networkSample.Sum) {{ [math]::Round(($networkSample.Sum * 8) / 1MB, 1) }} else {{ $null }}
        $caGenInstalled = $false
        $caGenVersion = 'Not inspected'
        $installedSoftware = @()
        $databaseRows = @()
        $instanceName = 'Unavailable'
        $sqlService = $null
        try {{
          $sqlService = Get-Service -ComputerName $computerName | Where-Object {{
            $_.Name -eq 'MSSQLSERVER' -or $_.Name -like 'MSSQL$*'
          }} | Sort-Object Name | Select-Object -First 1
        }} catch {{
          $sqlService = $null
        }}
        if ($sqlService) {{
          $instanceName = if ($sqlService.Name -eq 'MSSQLSERVER') {{ 'MSSQLSERVER' }} else {{ $sqlService.Name.Substring(6) }}
          $serverInstance = if ($instanceName -eq 'MSSQLSERVER') {{ $computerName }} else {{ "$computerName\\$instanceName" }}
          $connectionString = "Server=$serverInstance;Database=master;Integrated Security=True;TrustServerCertificate=True;Connect Timeout=5;"
          $sqlQuery = @"
SELECT
  CAST(SERVERPROPERTY('Edition') AS nvarchar(256)) AS Edition,
  CAST(SERVERPROPERTY('Collation') AS nvarchar(256)) AS Collation,
  CAST(SERVERPROPERTY('InstanceDefaultDataPath') AS nvarchar(512)) AS DataPath,
  CAST(SERVERPROPERTY('InstanceDefaultLogPath') AS nvarchar(512)) AS LogPath,
  CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS nvarchar(512)) AS BackupPath,
  CAST((
    SELECT TOP 1 LEFT(physical_name, LEN(physical_name) - CHARINDEX('\', REVERSE(physical_name)) + 1)
    FROM sys.master_files
    WHERE database_id = DB_ID('tempdb')
    ORDER BY file_id
  ) AS nvarchar(512)) AS TempDbPath,
  CAST((
    SELECT TOP 1 value_in_use
    FROM sys.configurations
    WHERE name = 'max server memory (MB)'
  ) AS nvarchar(128)) AS MaxServerMemoryMb,
  CAST((
    SELECT TOP 1 value_in_use
    FROM sys.configurations
    WHERE name = 'max degree of parallelism'
  ) AS nvarchar(128)) AS MaxDop,
  CAST((
    SELECT TOP 1 value_in_use
    FROM sys.configurations
    WHERE name = 'cost threshold for parallelism'
  ) AS nvarchar(128)) AS CostThreshold,
  CAST((
    SELECT compatibility_level
    FROM sys.databases
    WHERE name = 'master'
  ) AS nvarchar(128)) AS CompatibilityLevel,
  CAST(DATABASEPROPERTYEX('master', 'Recovery') AS nvarchar(128)) AS RecoveryModel,
  CAST((
    SELECT CONVERT(nvarchar(19), MAX(backup_finish_date), 120)
    FROM msdb.dbo.backupset
    WHERE type = 'D'
  ) AS nvarchar(128)) AS LastFullBackup,
  CAST((
    SELECT CAST(SUM(size) * 8.0 / 1024 / 1024 AS decimal(18,1))
    FROM sys.master_files
    WHERE database_id > 4
  ) AS nvarchar(128)) AS DatabaseSizeGb,
  CAST(REPLACE(REPLACE(@@VERSION, CHAR(13), ' '), CHAR(10), ' ') AS nvarchar(1000)) AS SqlServerVersion
"@
          try {{
            $connection = New-Object System.Data.SqlClient.SqlConnection $connectionString
            $command = $connection.CreateCommand()
            $command.CommandText = $sqlQuery
            $command.CommandTimeout = 5
            $adapter = New-Object System.Data.SqlClient.SqlDataAdapter $command
            $dataset = New-Object System.Data.DataSet
            [void]$adapter.Fill($dataset)
            $connection.Close()
            if ($dataset.Tables.Count -gt 0 -and $dataset.Tables[0].Rows.Count -gt 0) {{
              $dbInfo = $dataset.Tables[0].Rows[0]
              $databaseRows = @(
                @{{ label = 'SQL Server Version'; value = [string]$dbInfo.SqlServerVersion; icon = 'database' }},
                @{{ label = 'Instance Name'; value = $instanceName; icon = 'database' }},
                @{{ label = 'Edition'; value = [string]$dbInfo.Edition; icon = 'database' }},
                @{{ label = 'Collation'; value = [string]$dbInfo.Collation; icon = 'database' }},
                @{{ label = 'Compatibility Level'; value = [string]$dbInfo.CompatibilityLevel; icon = 'database' }},
                @{{ label = 'Recovery Model'; value = [string]$dbInfo.RecoveryModel; icon = 'database' }},
                @{{ label = 'Data Path'; value = [string]$dbInfo.DataPath; icon = 'folder' }},
                @{{ label = 'Log Path'; value = [string]$dbInfo.LogPath; icon = 'folder' }},
                @{{ label = 'Backup Path'; value = [string]$dbInfo.BackupPath; icon = 'folder' }},
                @{{ label = 'TempDB Path'; value = [string]$dbInfo.TempDbPath; icon = 'folder' }},
                @{{ label = 'Max Server Memory'; value = if ($dbInfo.MaxServerMemoryMb) {{ "$([int]$dbInfo.MaxServerMemoryMb) MB" }} else {{ 'Unavailable' }}; icon = 'database' }},
                @{{ label = 'Max Degree of Parallelism'; value = [string]$dbInfo.MaxDop; icon = 'database' }},
                @{{ label = 'Cost Threshold for Parallelism'; value = [string]$dbInfo.CostThreshold; icon = 'database' }},
                @{{ label = 'Last Full Backup'; value = if ($dbInfo.LastFullBackup) {{ [string]$dbInfo.LastFullBackup }} else {{ 'Unavailable' }}; icon = 'database' }},
                @{{ label = 'Database Size'; value = if ($dbInfo.DatabaseSizeGb) {{ "$([decimal]$dbInfo.DatabaseSizeGb) GB" }} else {{ 'Unavailable' }}; icon = 'database' }}
              )
            }}
          }} catch {{
            $databaseRows = @(
              @{{ label = 'SQL Server Version'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Instance Name'; value = $instanceName; icon = 'database' }},
              @{{ label = 'Edition'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Collation'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Compatibility Level'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Recovery Model'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Data Path'; value = 'Unavailable'; icon = 'folder' }},
              @{{ label = 'Log Path'; value = 'Unavailable'; icon = 'folder' }},
              @{{ label = 'Backup Path'; value = 'Unavailable'; icon = 'folder' }},
              @{{ label = 'TempDB Path'; value = 'Unavailable'; icon = 'folder' }},
              @{{ label = 'Max Server Memory'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Max Degree of Parallelism'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Cost Threshold for Parallelism'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Last Full Backup'; value = 'Unavailable'; icon = 'database' }},
              @{{ label = 'Database Size'; value = 'Unavailable'; icon = 'database' }}
            )
          }} finally {{
            if ($connection) {{ $connection.Dispose() }}
          }}
        }}
        if ($computerName -eq $env:COMPUTERNAME) {{
          $uninstallPaths = @(
            'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',
            'HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'
          )
          $softwareRows = @(Get-ItemProperty -Path $uninstallPaths -ErrorAction SilentlyContinue |
            Where-Object {{ $_.DisplayName }} |
            Select-Object DisplayName, DisplayVersion |
            Sort-Object DisplayName -Unique)
          $installedSoftware = @($softwareRows | ForEach-Object {{
            if ($_.DisplayVersion) {{ "$($_.DisplayName) ($($_.DisplayVersion))" }} else {{ "$($_.DisplayName)" }}
          }})
          $caGenRow = $softwareRows | Where-Object {{ $_.DisplayName -match 'CA\\s*Gen|CA GEN|AllFusion Gen' }} | Select-Object -First 1
          if ($caGenRow) {{
            $caGenInstalled = $true
            $caGenVersion = if ($caGenRow.DisplayVersion) {{ "$($caGenRow.DisplayVersion)" }} else {{ 'Installed' }}
          }}
        }}
        if (-not $databaseRows -or $databaseRows.Count -eq 0) {{
          $databaseRows = @(
            @{{ label = 'SQL Server Version'; value = 'SQL Server not detected'; icon = 'database' }},
            @{{ label = 'Instance Name'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Edition'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Collation'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Compatibility Level'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Recovery Model'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Data Path'; value = 'Unavailable'; icon = 'folder' }},
            @{{ label = 'Log Path'; value = 'Unavailable'; icon = 'folder' }},
            @{{ label = 'Backup Path'; value = 'Unavailable'; icon = 'folder' }},
            @{{ label = 'TempDB Path'; value = 'Unavailable'; icon = 'folder' }},
            @{{ label = 'Max Server Memory'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Max Degree of Parallelism'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Cost Threshold for Parallelism'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Last Full Backup'; value = 'Unavailable'; icon = 'database' }},
            @{{ label = 'Database Size'; value = 'Unavailable'; icon = 'database' }}
          )
        }}
        @{{
          computerName = $computerName
          checkedAt = '{checked_at}'
          uptimeDisplay = "{{0}}d {{1}}h {{2}}m" -f [int]$uptime.TotalDays, $uptime.Hours, $uptime.Minutes
          osCaption = $osInfo.Caption
          osArchitecture = $osInfo.OSArchitecture
          manufacturer = $computerSystem.Manufacturer
          model = $computerSystem.Model
          logicalCpuCount = if ($logicalCpuCount) {{ [int]$logicalCpuCount }} else {{ 0 }}
          iisInstalled = [bool]$iisService
          caGenInstalled = [bool]$caGenInstalled
          caGenVersion = $caGenVersion
          cpuPercent = [math]::Round($cpuInfo.Average, 0)
          totalMemoryGb = $totalMemoryGb
          usedMemoryGb = $usedMemoryGb
          networkMbps = $networkMbps
          totalSwapGb = if ($pageFileTotal) {{ [math]::Round($pageFileTotal / 1024, 1) }} else {{ 0 }}
          usedSwapGb = if ($pageFileUsed) {{ [math]::Round($pageFileUsed / 1024, 1) }} else {{ 0 }}
          storage = $disks
          serviceStatuses = $serviceRows
          databaseDetails = $databaseRows
          installedSoftware = $installedSoftware
        }} | ConvertTo-Json -Depth 5 -Compress
        """
    )

    storage = [
        StorageVolume(
            name=str(item.get("name", "Disk")),
            total_gb=_to_float(item.get("totalGb")),
            free_gb=_to_float(item.get("freeGb")),
            used_gb=_to_float(item.get("usedGb")),
            used_percent=int(round(_to_float(item.get("usedPercent")))),
        )
        for item in _ensure_list(payload.get("storage"))
    ]

    services = [
        ServiceStatus(
            name=str(item.get("name", "Service")),
            status=str(item.get("status", "Stopped")),
            uptime=str(item.get("uptime", "-")),
        )
        for item in _ensure_list(payload.get("serviceStatuses"))
    ]

    database_details = [
        DatabaseDetail(
            label=str(item.get("label", "")),
            value=_clean_text(item.get("value", "")),
            icon=str(item.get("icon", "database")),
        )
        for item in _ensure_list(payload.get("databaseDetails"))
    ]
    for detail in database_details:
        if detail.label == "Compatibility Level" and detail.value not in {"Unavailable", ""}:
            detail.value = f"{detail.value} ({_sql_version_name(detail.value)})"

    snapshot = Snapshot(
        computer_name=str(payload.get("computerName", normalized or os.environ.get("COMPUTERNAME", "Unavailable"))),
        primary_ip=normalized or _local_ip(),
        checked_at=str(payload.get("checkedAt", checked_at)),
        uptime_display=str(payload.get("uptimeDisplay", "Unavailable")),
        os_caption=str(payload.get("osCaption", "Unavailable")),
        os_architecture=str(payload.get("osArchitecture", "Unavailable")),
        manufacturer=str(payload.get("manufacturer", "Unavailable")),
        model=str(payload.get("model", "Unavailable")),
        logical_cpu_count=int(_to_float(payload.get("logicalCpuCount"))),
        iis_installed=bool(payload.get("iisInstalled", False)),
        ca_gen_installed=bool(payload.get("caGenInstalled", False)),
        ca_gen_version=str(payload.get("caGenVersion", "Not inspected")),
        cpu_percent=_to_float(payload.get("cpuPercent")),
        total_memory_gb=_to_float(payload.get("totalMemoryGb")),
        used_memory_gb=_to_float(payload.get("usedMemoryGb")),
        network_mbps=None if payload.get("networkMbps") is None else _to_float(payload.get("networkMbps")),
        total_swap_gb=_to_float(payload.get("totalSwapGb")),
        used_swap_gb=_to_float(payload.get("usedSwapGb")),
        storage=storage,
        service_statuses=services,
        database_details=database_details,
        installed_software=[str(item) for item in _ensure_list(payload.get("installedSoftware"))],
    )
    if normalized and (
        snapshot.os_caption == "Unavailable"
        or snapshot.total_memory_gb <= 0
        or snapshot.logical_cpu_count <= 0
        or not snapshot.storage
    ):
        logger.error(
            "Remote inspection returned incomplete core data for target=%s os=%s memory=%.1f cpu_count=%d disks=%d",
            normalized,
            snapshot.os_caption,
            snapshot.total_memory_gb,
            snapshot.logical_cpu_count,
            len(snapshot.storage),
        )
        raise RuntimeError(
            f"Unable to collect core system data from {normalized}. "
            "Check WMI/CIM access, firewall rules, and permissions on the remote server."
        )
    logger.info(
        "Inspection payload parsed for target=%s computer=%s sql_details=%d services=%d",
        normalized or "local machine",
        snapshot.computer_name,
        len(snapshot.database_details),
        len(snapshot.service_statuses),
    )
    return snapshot


def build_metrics(snapshot: Snapshot) -> list[Metric]:
    metrics = [
        Metric("CPU Usage", f"{int(round(snapshot.cpu_percent))}%", max(0, min(100, int(round(snapshot.cpu_percent)))), "0", "100 %"),
        Metric(
            "RAM Usage",
            f"{_round1(snapshot.used_memory_gb)}GB",
            int(round((snapshot.used_memory_gb / snapshot.total_memory_gb) * 100)) if snapshot.total_memory_gb else 0,
            "0",
            f"{_round1(snapshot.total_memory_gb)} GB",
        ),
    ]
    for disk in snapshot.storage:
        metrics.append(
            Metric(
                disk.name,
                f"{_round1(disk.used_gb)}GB",
                max(0, min(100, int(disk.used_percent))),
                "0",
                f"{_round1(disk.total_gb)} GB",
                "amber" if disk.used_percent >= 80 else "green",
            )
        )
    metrics.extend(
        [
            Metric(
                "Network I/O",
                f"{_round1(snapshot.network_mbps)}Mbps" if snapshot.network_mbps is not None else "Unavailable",
                max(0, min(100, int(round((snapshot.network_mbps or 0) / 1000 * 100)))),
                "0",
                "1000 Mbps",
            ),
            Metric(
                "Swap Usage",
                f"{_round1(snapshot.used_swap_gb)}GB",
                int(round((snapshot.used_swap_gb / snapshot.total_swap_gb) * 100)) if snapshot.total_swap_gb else 0,
                "0",
                f"{_round1(snapshot.total_swap_gb)} GB",
            ),
        ]
    )
    return metrics


def build_requirements(snapshot: Snapshot) -> list[RequirementRow]:
    server_name = snapshot.computer_name if snapshot.computer_name and snapshot.computer_name != "Unavailable" else snapshot.primary_ip
    description = " ".join(part for part in [snapshot.manufacturer, snapshot.model] if part and part != "Unavailable").strip() or "Not inspected"
    rows = [
        RequirementRow("Server", "", server_name or "Not inspected", bool(server_name and server_name != "Unavailable")),
        RequirementRow("Server Description", "", description, description != "Not inspected"),
        RequirementRow(
            "Virtual Cores",
            ">= 8 vCores",
            f"{snapshot.logical_cpu_count} vCores" if snapshot.logical_cpu_count else "Not inspected",
            snapshot.logical_cpu_count >= 8,
        ),
        RequirementRow(
            "Windows Bit (64 or 32)",
            "",
            snapshot.os_architecture or "Not inspected",
            bool(snapshot.os_architecture and snapshot.os_architecture != "Unavailable"),
        ),
        RequirementRow("If IIS Installed", "", "Yes" if snapshot.iis_installed else "No", True),
        RequirementRow(
            "CA GEN",
            "8.5 and above",
            snapshot.ca_gen_version if snapshot.ca_gen_installed else "Not detected",
            snapshot.ca_gen_installed and _ca_gen_version_ok(snapshot.ca_gen_version),
        ),
        RequirementRow(
            "Operating System",
            "Windows 2022 64bit",
            snapshot.os_caption or "Not inspected",
            "2022" in snapshot.os_caption and "64" in snapshot.os_architecture,
        ),
        RequirementRow(
            "CPU Cores",
            ">= 8 cores",
            f"{snapshot.logical_cpu_count} cores" if snapshot.logical_cpu_count else "Not inspected",
            snapshot.logical_cpu_count >= 8,
        ),
        RequirementRow(
            "RAM",
            ">= 16 GB",
            f"{_round1(snapshot.total_memory_gb)} GB" if snapshot.total_memory_gb else "Not inspected",
            snapshot.total_memory_gb >= 16,
        ),
    ]
    for disk in snapshot.storage:
        rows.append(
            RequirementRow(
                disk.name,
                ">= 200 GB",
                f"{_round1(disk.total_gb)} GB total, {_round1(disk.free_gb)} GB free",
                disk.total_gb >= 200,
            )
        )
    return rows


def _ca_gen_version_ok(version: str) -> bool:
    current = ""
    for char in version:
        if char.isdigit() or (char == "." and current):
            current += char
        elif current:
            break
    if not current:
        return False
    try:
        return float(current) >= 8.5
    except ValueError:
        return False
