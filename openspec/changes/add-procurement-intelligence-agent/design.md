# Design: add-procurement-intelligence-agent

## Overview
The procurement intelligence agent is a Pydantic AI workflow that performs four independent checks,
normalizes their outcomes, and emits one structured recommendation with a deterministic decision
priority policy.

## Architecture
Components:
- `models.py`
  - `PurchaseRequest`: validated input schema (Pydantic v2)
  - `ProcurementRecommendation`: validated output schema (Pydantic v2)
- `data/loader.py`
  - sole access path for mock fixture retrieval
- `tools/`
  - `check_budget`
  - `check_vendor_duplication`
  - `check_policy_compliance`
  - `assess_risk`
- `agent.py`
  - Pydantic AI agent with `output_type=ProcurementRecommendation`
  - orchestration across all four tools

## Decision Resolution
Each check yields a status that maps to one of three decision levels:
- escalate-level signals: uncertain data, high risk, or tool execution failure
- deny-level signals: explicit policy or budget rejection conditions
- approve-level signals: no deny/escalate signals raised

Final decision is computed by strict priority:
1. `escalate` if any escalate-level signal exists
2. otherwise `deny` if any deny-level signal exists
3. otherwise `approve`

This ensures safety-first behavior and deterministic outcomes.

## Tool Selection and Invocation
The agent must run all four tools for every request. The final rationale should summarize each
check outcome and identify which checks drove the final recommendation.

Tool docstrings must be explicit enough for reliable selection by Pydantic AI, but implementation
should still register tools directly with the agent to avoid ambiguity.

## Error Handling
Tool failures are non-fatal to overall recommendation generation.
- Each tool call is wrapped in exception handling.
- On exception, agent records a failure note for that check.
- Any tool failure raises an escalate-level signal.
- The final rationale must include the failing tool name and failure summary.

## Validation Strategy
- Input is validated against `PurchaseRequest` before orchestration.
- Output is schema-constrained via `output_type=ProcurementRecommendation`.
- Recommendation rationale must be non-empty after trimming whitespace.
- Recommendation decision is constrained to `approve | deny | escalate`.

## Non-Goals
- No direct JSON reads from `mock_data/` in tools or agent.
- No autonomous final purchasing decision; output remains advisory.
