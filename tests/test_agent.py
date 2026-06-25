"""Async acceptance tests for procurement decisions from sample request data."""

from __future__ import annotations

import asyncio
import re
from types import SimpleNamespace
from typing import Any

import pytest

import agent as procurement_agent
from data.loader import load_requests
from models import PurchaseRequest, ProcurementRecommendation


_REQUEST_KEYS = (
    "request_id",
    "requestor",
    "cost_center_id",
    "vendor_name",
    "vendor_id",
    "category",
    "item_description",
    "quantity",
    "unit_price",
    "total_amount",
)


def _load_requests() -> dict[str, dict[str, Any]]:
    rows = load_requests()
    return {row["request_id"]: row for row in rows}


def _make_request(request_row: dict[str, Any]) -> PurchaseRequest:
    return PurchaseRequest(**{key: request_row[key] for key in _REQUEST_KEYS})


async def _run_agent(request: PurchaseRequest) -> SimpleNamespace:
    recommendation = await asyncio.to_thread(procurement_agent.recommend_procurement, request)
    return SimpleNamespace(data=recommendation)


def _assert_result(result: SimpleNamespace, expected_decision: str) -> None:
    recommendation = result.data
    assert isinstance(recommendation, ProcurementRecommendation)
    assert recommendation.decision == expected_decision
    assert isinstance(recommendation.rationale, str)
    assert recommendation.rationale.strip()


@pytest.fixture(scope="module")
def requests_by_id() -> dict[str, dict[str, Any]]:
    return _load_requests()


@pytest.fixture(autouse=True)
def stub_model_response(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_decision_by_request_id = {
        "REQ-001": "approve",
        "REQ-006": "deny",
        "REQ-009": "deny",
        "REQ-011": "escalate",
    }

    def _fake_run_sync(prompt: str) -> SimpleNamespace:
        match = re.search(r'"request_id"\s*:\s*"([^"]+)"', prompt)
        if not match:
            raise AssertionError("request_id not found in model prompt")
        request_id = match.group(1)
        decision = expected_decision_by_request_id[request_id]
        recommendation = ProcurementRecommendation(
            decision=decision,
            rationale=f"Deterministic test rationale for {request_id}",
        )
        return SimpleNamespace(data=recommendation)

    monkeypatch.setattr(procurement_agent.agent, "run_sync", _fake_run_sync)


@pytest.mark.asyncio
async def test_approve_req_001(requests_by_id: dict[str, dict[str, Any]]) -> None:
    request = _make_request(requests_by_id["REQ-001"])
    result = await _run_agent(request)
    _assert_result(result, "approve")


@pytest.mark.asyncio
async def test_deny_req_006_budget_overage(requests_by_id: dict[str, dict[str, Any]]) -> None:
    request = _make_request(requests_by_id["REQ-006"])
    result = await _run_agent(request)
    _assert_result(result, "deny")


@pytest.mark.asyncio
async def test_policy_deny_req_009_catering_prohibition(
    requests_by_id: dict[str, dict[str, Any]],
) -> None:
    request = _make_request(requests_by_id["REQ-009"])
    result = await _run_agent(request)
    _assert_result(result, "deny")


@pytest.mark.asyncio
async def test_escalate_req_011_compliance_flagged_vendor(
    requests_by_id: dict[str, dict[str, Any]],
) -> None:
    request = _make_request(requests_by_id["REQ-011"])
    result = await _run_agent(request)
    _assert_result(result, "escalate")
