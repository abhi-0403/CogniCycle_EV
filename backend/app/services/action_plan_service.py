import logging
from app.agents.action_plan_agent import ActionPlanAgent
from app.schemas.action_plan import ActionPlanRequest, DynamicActionPlan
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


class ActionPlanService:
    """Service handling dynamic on-demand action plan generation with persistent caching."""

    def __init__(self) -> None:
        self.agent = ActionPlanAgent()
        self.storage = StorageService()

    def generate_plan(self, req: ActionPlanRequest) -> DynamicActionPlan:
        asset_id = getattr(req.asset, "asset_id", None)
        
        # 1. Check cache first if not forcing regeneration
        if asset_id and not req.force_regenerate:
            cached = self.storage.get_action_plan(asset_id)
            if cached:
                logger.info(f"Returning cached action plan for {asset_id} (0 LLM calls needed)")
                plan_obj = DynamicActionPlan.model_validate(cached)
                plan_obj.is_cached = True
                return plan_obj

        # 2. Invoke LLM with component context
        plan = self.agent.generate_plan(
            asset=req.asset,
            decision=req.decision,
            confidence=req.confidence or 0.85,
            safety_status=req.safety_status or "SAFE",
            reasoning=req.reasoning or ""
        )

        # 3. Persist into backend/data/output/action_plans.json
        if asset_id:
            self.storage.save_action_plan(asset_id, plan.model_dump())

        return plan

    def get_all_plans(self):
        return self.storage.get_all_action_plans()
