from typing import Any, Dict
from app.agents.universal_triage_agent import UniversalTriageAgent, UniversalAssessment


class UniversalTriageService:
    """Service providing domain telemetry analysis across all 7 pillars of EV components."""

    def __init__(self) -> None:
        self.agent = UniversalTriageAgent()

    def analyze_asset(self, asset: Dict[str, Any], domain: str = "Battery & Energy Storage") -> UniversalAssessment:
        return self.agent.analyze(asset, domain=domain)
