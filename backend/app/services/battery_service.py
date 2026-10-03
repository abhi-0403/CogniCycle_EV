from typing import Any, Dict

from app.agents.battery_agent import BatteryAgent
from app.schemas.battery import BatteryAssessment


class BatteryService:
    """
    Service layer for Battery & Energy Storage operations.

    The service coordinates domain-agent execution and provides
    a clean interface for the API layer.
    """

    def __init__(self) -> None:
        self.agent = BatteryAgent()

    def analyze_asset(self, asset: Dict[str, Any]) -> BatteryAssessment:
        """
        Analyse a single battery asset using the Battery Domain Agent.
        """

        if not asset:
            raise ValueError("Battery asset data cannot be empty.")

        return self.agent.analyze(asset)