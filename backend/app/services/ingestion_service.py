import json
from pathlib import Path
from typing import List

from app.schemas.asset import Asset


class IngestionService:
    """Service to load and parse assets from the operational dataset."""

    def __init__(self, file_path: str = None) -> None:
        if file_path:
            self.file_path = Path(file_path)
        else:
            # Default to backend/data/input/assets.json
            project_root = Path(__file__).resolve().parents[2]
            self.file_path = project_root / "data" / "input" / "assets.json"

    def load_assets(self) -> List[Asset]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Dataset must be a list of assets.")

        return [Asset(**item) for item in data]
