import json
from pathlib import Path

from app.services.battery_service import BatteryService


def load_first_battery_asset():
    """Load the first battery asset from the real input dataset."""

    project_root = Path(__file__).resolve().parents[1]
    assets_file = project_root / "data" / "input" / "assets.json"

    with open(assets_file, "r", encoding="utf-8") as file:
        assets = json.load(file)

    for asset in assets:
        if asset.get("component", "").lower() == "battery module":
            return asset

    raise RuntimeError("No Battery Module found in assets.json")


from unittest.mock import patch
from app.schemas.battery import BatteryAssessment

def test_battery_service():
    """Test the Battery Service with a real battery asset."""

    asset = load_first_battery_asset()

    service = BatteryService()
    
    mock_assessment = BatteryAssessment(
        agent_name="battery_agent",
        domain="Battery & Energy Storage",
        assessment="MOCKED ASSESSMENT",
        condition_summary="MOCKED CONDITION",
        technical_findings=[],
        safety_risks=[],
        reuse_potential="LOW",
        refurbishment_potential="HIGH",
        recycling_considerations=[],
        missing_information=[],
        evidence_requests=[],
        risk_flags=[],
        confidence=0.8,
        reasoning_summary="MOCKED REASONING",
    )
    
    with patch("app.services.battery_service.BatteryAgent.analyze", return_value=mock_assessment):
        result = service.analyze_asset(asset)

    print("\n========== BATTERY SERVICE RESULT ==========\n")
    print(result.model_dump_json(indent=2))
    print("\n============================================\n")

    assert result.agent_name == "battery_agent"
    assert result.domain == "Battery & Energy Storage"
    assert result.assessment
    assert 0.0 <= result.confidence <= 1.0