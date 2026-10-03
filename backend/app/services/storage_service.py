import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StorageService:
    """Manages persistent caching for analyzed assets, action plans, and uploaded datasets."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[2]
        self.data_dir = self.project_root / "data"
        self.input_dir = self.data_dir / "input"
        self.output_dir = self.data_dir / "output"

        self.default_assets_file = self.input_dir / "assets.json"
        self.uploaded_assets_file = self.input_dir / "uploaded_assets.json"
        self.analyzed_file = self.output_dir / "analyzed_assets.json"
        self.action_plans_file = self.output_dir / "action_plans.json"

    def ensure_output_dir(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def has_analyzed_assets(self) -> bool:
        """Check if pre-analyzed assets file exists and is non-empty."""
        return self.analyzed_file.exists() and self.analyzed_file.stat().st_size > 5

    def load_analyzed_assets(self) -> Optional[List[Dict[str, Any]]]:
        """Load pre-analyzed results if available."""
        if not self.has_analyzed_assets():
            return None
        try:
            with open(self.analyzed_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception as e:
            logger.warning(f"Failed to read analyzed_assets.json: {e}")
        return None

    def save_analyzed_assets(self, items: List[Dict[str, Any]]) -> None:
        """Persist analyzed decisions to backend/data/output/analyzed_assets.json."""
        self.ensure_output_dir()
        try:
            with open(self.analyzed_file, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
            logger.info(f"Saved {len(items)} analyzed records to {self.analyzed_file}")
        except Exception as e:
            logger.error(f"Error saving analyzed assets: {e}")

    def clear_output(self) -> bool:
        """Clear the output directory (used when user resets or uploads new data)."""
        try:
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                logger.info("Cleared backend/data/output directory.")
            return True
        except Exception as e:
            logger.error(f"Error clearing output directory: {e}")
            return False

    def get_action_plan(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached action plan for an asset_id if previously generated."""
        if not self.action_plans_file.exists():
            return None
        try:
            with open(self.action_plans_file, "r", encoding="utf-8") as f:
                plans = json.load(f)
            if isinstance(plans, dict) and asset_id in plans:
                return plans[asset_id]
        except Exception as e:
            logger.warning(f"Error loading cached action plan for {asset_id}: {e}")
        return None

    def save_action_plan(self, asset_id: str, plan_dict: Dict[str, Any]) -> None:
        """Persist generated LLM action plan so future clicks never trigger redundant calls."""
        self.ensure_output_dir()
        plans = {}
        if self.action_plans_file.exists():
            try:
                with open(self.action_plans_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    plans = data
            except Exception:
                plans = {}

        plans[asset_id] = plan_dict
        try:
            with open(self.action_plans_file, "w", encoding="utf-8") as f:
                json.dump(plans, f, indent=2)
            logger.info(f"Cached action plan for asset {asset_id}")
        except Exception as e:
            logger.error(f"Failed to persist action plan for {asset_id}: {e}")

    def get_all_action_plans(self) -> Dict[str, Any]:
        """Return all persisted action plans."""
        if not self.action_plans_file.exists():
            return {}
        try:
            with open(self.action_plans_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save_uploaded_dataset(self, assets_list: List[Dict[str, Any]]) -> Path:
        """Save an uploaded dataset to backend/data/input/uploaded_assets.json."""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        # Ensure every item has an asset_id
        for i, item in enumerate(assets_list, 1):
            if not item.get("asset_id"):
                comp = (item.get("component") or "ITEM").replace(" ", "-").upper()[:3]
                item["asset_id"] = f"EV-UP-{comp}-{i:03d}"

        with open(self.uploaded_assets_file, "w", encoding="utf-8") as f:
            json.dump(assets_list, f, indent=2)
        return self.uploaded_assets_file
