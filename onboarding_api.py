"""Onboarding API router for merchant setup submissions."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field, condecimal


class OnboardingCreate(BaseModel):
    store_name: str = Field(..., min_length=1, max_length=200)
    owner_email: EmailStr
    store_type: str = Field(..., min_length=1, max_length=100)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    description: str = Field(..., min_length=1, max_length=5000)
    channels: list[str] = Field(..., min_length=1, max_length=10)
    catalog_size: str = Field(..., min_length=1, max_length=100)
    order_volume: str = Field(..., min_length=1, max_length=100)
    payments: list[str] = Field(..., min_length=1, max_length=10)
    risk_mode: str = Field(..., min_length=1, max_length=200)
    approval_limit: condecimal(ge=0, max_digits=12, decimal_places=2)
    readiness_checks: list[str] = Field(default_factory=list, max_length=20)
    launch_goal: str | None = Field(default=None, max_length=2000)


class OnboardingStore:
    def __init__(self) -> None:
        self.memory: list[dict[str, Any]] = []

    @staticmethod
    def submission_id() -> str:
        return f"onb_{secrets.token_urlsafe(12)}"

    async def create(self, db: Any, data: OnboardingCreate) -> dict[str, Any]:
        submission = data.model_dump(mode="json")
        submission.update(
            {
                "id": self.submission_id(),
                "status": "submitted",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        if db and getattr(db, "connected", False):
            await db.create("onboarding_submissions", submission, id=submission["id"])
        else:
            self.memory.append(submission)
        return submission

    async def list(self, db: Any) -> Any:
        if db and getattr(db, "connected", False):
            return await db.select("onboarding_submissions", limit=100)
        return {"items": self.memory}


def build_onboarding_router(get_db, require_user, require_admin) -> APIRouter:
    router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])
    store = OnboardingStore()

    @router.post("", dependencies=[Depends(require_user)])
    async def create_onboarding_submission(data: OnboardingCreate):
        submission = await store.create(get_db(), data)
        return {
            "status": "submitted",
            "submission_id": submission["id"],
            "next_steps": [
                "review_configuration",
                "connect_store",
                "configure_payments",
                "run_launch_checks",
            ],
        }

    @router.get("", dependencies=[Depends(require_admin)])
    async def list_onboarding_submissions():
        return await store.list(get_db())

    return router
