from __future__ import annotations

import time

from .models import CommandPolicy, FaultMessage, TelemetryPayload


class SafetyManager:
    def __init__(self, low_battery_threshold: float = 15.0) -> None:
        self.low_battery_threshold = low_battery_threshold
        self.estop_triggered = False
        self.active_faults: list[FaultMessage] = []

    def trigger_estop(self) -> FaultMessage:
        self.estop_triggered = True
        fault = FaultMessage(
            severity='critical',
            code='ESTOP_TRIGGERED',
            message='Emergency stop is active',
            timestamp=time.time(),
        )
        self._upsert_fault(fault)
        return fault

    def clear_estop(self) -> None:
        self.estop_triggered = False
        self.active_faults = [fault for fault in self.active_faults if fault.code != 'ESTOP_TRIGGERED']

    def evaluate(self, telemetry: TelemetryPayload) -> list[FaultMessage]:
        faults: list[FaultMessage] = []
        if telemetry.battery_level <= self.low_battery_threshold:
            faults.append(FaultMessage(
                severity='warning',
                code='LOW_BATTERY',
                message='Battery below safe threshold',
                timestamp=time.time(),
            ))
        if self.estop_triggered:
            faults.append(FaultMessage(
                severity='critical',
                code='ESTOP_TRIGGERED',
                message='Emergency stop is active',
                timestamp=time.time(),
            ))
        self.active_faults = []
        for fault in faults:
            self._upsert_fault(fault)
        return self.active_faults.copy()

    def policy(self, telemetry: TelemetryPayload) -> CommandPolicy:
        faults = self.evaluate(telemetry)
        critical = any(f.severity == 'critical' for f in faults)
        if critical:
            return CommandPolicy(allowed_categories=['always'], restricted=True)
        if any(f.code == 'LOW_BATTERY' for f in faults):
            return CommandPolicy(allowed_categories=['motion', 'behavior', 'mission', 'plugin', 'always'], restricted=True)
        return CommandPolicy(allowed_categories=['motion', 'behavior', 'mission', 'plugin', 'body', 'script', 'arm', 'bt', 'always'], restricted=False)

    def _upsert_fault(self, fault: FaultMessage) -> None:
        self.active_faults = [existing for existing in self.active_faults if existing.code != fault.code]
        self.active_faults.append(fault)
