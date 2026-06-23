# Tasks: add-procurement-intelligence-agent

## 1. Models and Contracts
- [ ] Create `models.py` with Pydantic v2 `PurchaseRequest` and `ProcurementRecommendation`
- [ ] Constrain `ProcurementRecommendation.decision` to `approve`, `deny`, or `escalate`
- [ ] Enforce non-empty rationale in output model validation

## 2. Data Access Layer
- [ ] Implement `data/loader.py` helpers for budgets, vendors, policies, and requests
- [ ] Ensure all tool data access flows through loader functions
- [ ] Confirm no tool or agent code reads files under `mock_data/` directly

## 3. Tool Implementations
- [ ] Implement `tools/budget.py` with `check_budget`
- [ ] Implement `tools/vendor_duplication.py` with `check_vendor_duplication`
- [ ] Implement `tools/policy_compliance.py` with `check_policy_compliance`
- [ ] Implement `tools/risk_assessment.py` with `assess_risk`
- [ ] Add clear docstrings for all public tool functions

## 4. Agent Orchestration
- [ ] Implement `agent.py` using `pydantic_ai.Agent(..., output_type=ProcurementRecommendation)`
- [ ] Register and call all four tools for every recommendation flow
- [ ] Apply final decision priority `escalate > deny > approve`
- [ ] Catch tool errors and include failure details in rationale

## 5. Tests
- [ ] Add tests for each tool success path under `tests/`
- [ ] Add agent tests covering approve, deny, and escalate scenarios
- [ ] Add tests validating non-empty rationale and constrained decision values
- [ ] Add a partial-data or tool-failure scenario that escalates with error rationale

## 6. Verification
- [ ] Run `openspec validate add-procurement-intelligence-agent`
- [ ] Run `pytest tests/ -v --tb=short --junitxml=docs/test-results.xml`
- [ ] Update Go/No-Go evidence with test and validation outcomes as needed
