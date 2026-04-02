from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from .app_logging import get_logger
from .inspector import inspect_target


class InspectionThread(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target

    def run(self) -> None:
        logger = get_logger()
        target_name = self.target or "local machine"
        logger.info("Inspection thread started for target=%s", target_name)
        try:
            snapshot = inspect_target(self.target)
            logger.info(
                "Inspection thread completed for target=%s cpu=%.1f memory=%.1fGB services=%d disks=%d",
                target_name,
                snapshot.cpu_percent,
                snapshot.total_memory_gb,
                len(snapshot.service_statuses),
                len(snapshot.storage),
            )
            self.completed.emit(snapshot)
        except Exception as error:  # noqa: BLE001
            logger.exception("Inspection thread failed for target=%s", target_name)
            self.failed.emit(str(error))
