from typing import Dict, Any, List
from app.schemas.asset import Asset
from app.schemas.decision import DecisionResult
from app.services.routing_service import RoutingService
from app.services.universal_triage_service import UniversalTriageService
from app.services.decision_engine import DecisionEngine


class PipelineService:
    """Orchestrates end-to-end evaluation across all 7 pillars of EV components."""

    def __init__(self):
        self.triage_service = UniversalTriageService()
        self.decision_engine = DecisionEngine()

    def process_asset(self, asset: Asset) -> DecisionResult:
        """
        1. Routing: Map component to one of 7 pillars
        2. Domain Analysis: Technical telemetry assessment
        3. Decision Engine: Grounded circular disposition routing
        """
        domain = RoutingService.determine_domain(asset)

        # Technical domain assessment for any of the 7 pillars
        assessment_model = self.triage_service.analyze_asset(asset.model_dump(), domain=domain)
        agent_assessment = assessment_model.model_dump()

        # Final pathway decision
        decision_result = self.decision_engine.evaluate(
            asset=asset,
            domain=domain,
            agent_assessment=agent_assessment
        )

        return decision_result

    def process_all_assets(self, assets: list[Asset]) -> list[Dict[str, Any]]:
        """Process an entire batch of assets and bundle raw context for instant UI retrieval."""
        results = []
        for asset in assets:
            res = self.process_asset(asset)
            res_dict = res.model_dump()
            res_dict["raw_asset"] = asset.model_dump()
            results.append(res_dict)
        return results
