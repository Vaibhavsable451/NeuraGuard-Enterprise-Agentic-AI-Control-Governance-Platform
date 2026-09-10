"""Human-in-the-loop Approval Queue for REVIEW_REQUIRED governance decisions."""
import time
import uuid
from app.storage import insert, all_records, update_one

EXPIRATION_SECONDS = 24 * 3600


def enqueue_approval(original_request: str, risk_score: int, agent_path: list[str], reason: str) -> dict:
    record = {
        "approval_id": f"appr_{uuid.uuid4().hex[:10]}",
        "original_request": original_request,
        "risk_score": risk_score,
        "agent_path": agent_path,
        "reason": reason,
        "status": "pending",
        "reviewer": None,
        "decision": None,
        "decision_reason": None,
        "created_at": time.time(),
        "decided_at": None,
        "expires_at": time.time() + EXPIRATION_SECONDS,
    }
    insert("approvals", record)
    return record


def list_pending() -> list[dict]:
    now = time.time()
    return [a for a in all_records("approvals") if a["status"] == "pending" and a["expires_at"] > now]


def list_all() -> list[dict]:
    return all_records("approvals")


def decide(approval_id: str, approve: bool, reviewer: str, reason: str) -> dict | None:
    status = "approved" if approve else "rejected"
    return update_one("approvals", "approval_id", approval_id, {
        "status": status, "decision": status, "reviewer": reviewer,
        "decision_reason": reason, "decided_at": time.time(),
    })
