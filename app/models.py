from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class StorageVolume:
    name: str
    total_gb: float
    free_gb: float
    used_gb: float
    used_percent: int


@dataclass(slots=True)
class ServiceStatus:
    name: str
    status: str
    uptime: str


@dataclass(slots=True)
class DatabaseDetail:
    label: str
    value: str
    icon: str = "database"


@dataclass(slots=True)
class RequirementRow:
    component: str
    required: str
    actual: str
    passed: bool


@dataclass(slots=True)
class Snapshot:
    computer_name: str = "Unavailable"
    primary_ip: str = "Unavailable"
    checked_at: str = "Unavailable"
    uptime_display: str = "Unavailable"
    os_caption: str = "Unavailable"
    os_architecture: str = "Unavailable"
    manufacturer: str = "Unavailable"
    model: str = "Unavailable"
    logical_cpu_count: int = 0
    iis_installed: bool = False
    ca_gen_installed: bool = False
    ca_gen_version: str = "Not inspected"
    cpu_percent: float = 0.0
    total_memory_gb: float = 0.0
    used_memory_gb: float = 0.0
    network_mbps: float | None = None
    total_swap_gb: float = 0.0
    used_swap_gb: float = 0.0
    storage: list[StorageVolume] = field(default_factory=list)
    service_statuses: list[ServiceStatus] = field(default_factory=list)
    database_details: list[DatabaseDetail] = field(default_factory=list)
    installed_software: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Metric:
    label: str
    display_value: str
    progress: int
    min_label: str
    max_label: str
    tone: str = "green"
