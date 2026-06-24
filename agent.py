"""Procurement intelligence agent orchestration and configuration."""

from __future__ import annotations

import json
import os
from typing import Literal

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()

OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY")
if OPENAI_API_KEY and "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def _normalize_model_name(model_name: str) -> str:
    """Map deprecated model prefixes to stable, explicit provider prefixes."""
    if model_name.startswith("openai:"):
        return "openai-chat:" + model_name.split(":", 1)[1]
    return model_name


MODEL_NAME = _normalize_model_name(
    os.getenv("PROCUREMENT_AGENT_MODEL", "openai-chat:gpt-4")
)

SYSTEM_PROMPT = """
You are the Procurement Intelligence Agent for FedEx procurement pre-screening.

You MUST evaluate one PurchaseRequest and produce a ProcurementRecommendation object.

Output constraints:
- decision must be exactly one of: approve, deny, escalate
- rationale must be a non-empty string

Mandatory tool workflow:
- Execute or attempt all four tools for every request:
  1) check_budget(cost_center_id, requested_amount)
  2) check_vendor_duplication(vendor_id, category, amount)
  3) check_policy_compliance(purchase_request)
  4) assess_risk(vendor_id)
- Do not stop after one finding; account for all checks in rationale.

Decision precedence (strict):
- If any check yields escalate-equivalent signal, final decision is escalate.
- Else if any check yields deny-equivalent signal, final decision is deny.
- Else final decision is approve.

Error handling:
- If any tool reports an error or a tool execution fails, include the failure detail in rationale.
- Never fail silently.
- Missing or failed check data must be treated as escalate-equivalent.

Rationale quality:
- Mention key findings from budget, policy, vendor duplication, and risk checks.
- Reference policy IDs where available.
- Keep rationale concise and audit-friendly.
""".strip()

agent: Agent[None, ProcurementRecommendation] = Agent(
    MODEL_NAME,
    output_type=ProcurementRecommendation,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        check_budget,
        check_vendor_duplication,
        check_policy_compliance,
        assess_risk,
    ],
)


Decision = Literal["approve", "deny", "escalate"]


def _record_tool_error(tool_name: str, exc: Exception) -> dict[str, object]:
    """Create a normalized tool-error payload used in decision/rationale synthesis."""
    return {
        "tool": tool_name,
        "error": f"{type(exc).__name__}: {exc}",
        "outcome": "escalate",
    }


def _collect_tool_results(purchase_request: PurchaseRequest) -> dict[str, dict[str, object]]:
    """Execute all four tools and return normalized result records."""
    results: dict[str, dict[str, object]] = {}

    try:
        results["budget"] = check_budget(
            cost_center_id=purchase_request.cost_center_id,
            requested_amount=purchase_request.total_amount,
        )
    except Exception as exc:
        results["budget"] = _record_tool_error("check_budget", exc)

    try:
        results["vendor_duplication"] = check_vendor_duplication(
            vendor_id=purchase_request.vendor_id,
            category=purchase_request.category,
            amount=purchase_request.total_amount,
        )
    except Exception as exc:
        results["vendor_duplication"] = _record_tool_error(
            "check_vendor_duplication",
            exc,
        )

    try:
        results["policy_compliance"] = check_policy_compliance(purchase_request)
    except Exception as exc:
        results["policy_compliance"] = _record_tool_error("check_policy_compliance", exc)

    try:
        results["risk"] = assess_risk(vendor_id=purchase_request.vendor_id)
    except Exception as exc:
        results["risk"] = _record_tool_error("assess_risk", exc)

    return results


def _derive_decision_candidates(tool_results: dict[str, dict[str, object]]) -> set[Decision]:
    """Map tool result payloads into comparable recommendation candidates."""
    candidates: set[Decision] = set()

    budget_result = tool_results.get("budget", {})
    if budget_result.get("error"):
        candidates.add("escalate")
    elif str(budget_result.get("outcome", "")).lower() == "deny":
        candidates.add("deny")

    vendor_result = tool_results.get("vendor_duplication", {})
    if vendor_result.get("error"):
        candidates.add("escalate")
    else:
        forced_decision = str(vendor_result.get("forced_decision", "")).lower()
        if forced_decision == "escalate":
            candidates.add("escalate")
        elif forced_decision == "deny":
            candidates.add("deny")

    policy_result = tool_results.get("policy_compliance", {})
    if policy_result.get("error"):
        candidates.add("escalate")
    else:
        policy_outcome = str(policy_result.get("outcome", "")).lower()
        if policy_outcome == "escalate":
            candidates.add("escalate")
        elif policy_outcome == "deny":
            candidates.add("deny")

    risk_result = tool_results.get("risk", {})
    if risk_result.get("error"):
        candidates.add("escalate")
    else:
        risk_level = str(risk_result.get("risk_level", "")).lower()
        if risk_level in {"critical", "high", "medium"}:
            candidates.add("escalate")

    if not candidates:
        candidates.add("approve")

    return candidates


def _resolve_final_decision(candidates: set[Decision]) -> Decision:
    """Resolve final recommendation using strict precedence rules."""
    if "escalate" in candidates:
        return "escalate"
    if "deny" in candidates:
        return "deny"
    return "approve"


def _fallback_recommendation(
    purchase_request: PurchaseRequest,
    tool_results: dict[str, dict[str, object]],
    model_error: Exception,
) -> ProcurementRecommendation:
    """Return schema-valid recommendation when the model call fails."""
    candidates = _derive_decision_candidates(tool_results)
    decision = _resolve_final_decision(candidates)

    error_sections: list[str] = []
    for tool_name, payload in tool_results.items():
        error_message = payload.get("error")
        if error_message:
            error_sections.append(f"{tool_name} failed: {error_message}")

    rationale_parts = [
        (
            f"Model execution failed for request {purchase_request.request_id}: "
            f"{type(model_error).__name__}: {model_error}."
        ),
        "All four tools were attempted and decision precedence escalate > deny > approve was applied.",
    ]
    if error_sections:
        rationale_parts.append("Tool failures: " + " | ".join(error_sections))

    rationale = " ".join(rationale_parts).strip()
    return ProcurementRecommendation(decision=decision, rationale=rationale)


def _build_user_prompt(
    purchase_request: PurchaseRequest,
    tool_results: dict[str, dict[str, object]],
) -> str:
    """Build a deterministic model input containing request and tool evidence."""
    request_json = purchase_request.model_dump_json(indent=2)
    results_json = json.dumps(tool_results, indent=2)

    return (
        "Evaluate this purchase request and return ProcurementRecommendation. "
        "Use strict decision precedence escalate > deny > approve.\n\n"
        f"PurchaseRequest:\n{request_json}\n\n"
        "The four required tool checks were executed/attempted with these results:\n"
        f"{results_json}\n\n"
        "Produce only schema-valid recommendation output."
    )


def recommend_procurement(purchase_request: PurchaseRequest) -> ProcurementRecommendation:
    """Evaluate a purchase request and return a typed procurement recommendation."""
    tool_results = _collect_tool_results(purchase_request)

    try:
        result = agent.run_sync(_build_user_prompt(purchase_request, tool_results))
        return result.data
    except Exception as exc:
        return _fallback_recommendation(purchase_request, tool_results, exc)
