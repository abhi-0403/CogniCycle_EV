import json
from pathlib import Path

from app.schemas.asset import Asset


def test_real_asset_matches_schema():
    """Validate a real asset from assets.json against the canonical schema."""

    project_root = Path(__file__).resolve().parents[1]
    assets_file = project_root / "data" / "input" / "assets.json"

    with open(assets_file, "r", encoding="utf-8") as file:
        assets = json.load(file)

    assert assets
    assert isinstance(assets, list)

    asset = Asset.model_validate(assets[0])

    assert asset.component is not None