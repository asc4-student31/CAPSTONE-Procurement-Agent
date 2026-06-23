# Capability: Procurement Intelligence Agent Wiring

## ADDED Requirements

### Requirement: Pydantic AI Agent with Structured Output
The system SHALL construct the procurement agent using `pydantic_ai.Agent` with
`output_type=ProcurementRecommendation`.

#### Scenario: Structured output contract is enforced
- GIVEN an agent recommendation run
- WHEN the model produces output
- THEN output is validated against `ProcurementRecommendation`

### Requirement: Four-check Orchestration
The agent SHALL invoke all four tools (`check_budget`, `check_vendor_duplication`,
`check_policy_compliance`, `assess_risk`) for each recommendation flow.

#### Scenario: All checks executed
- GIVEN a valid purchase request
- WHEN the recommendation flow runs
- THEN each of the four tools is called exactly once unless an unrecoverable pre-validation error occurs

### Requirement: Decision Priority Policy
The final recommendation SHALL apply deterministic decision priority in this order:
`escalate` > `deny` > `approve`.

#### Scenario: Escalate overrides deny and approve
- GIVEN at least one escalate-level signal and any number of deny/pass signals
- WHEN final decision is resolved
- THEN decision is `escalate`

#### Scenario: Deny overrides approve
- GIVEN no escalate-level signals and at least one deny-level signal
- WHEN final decision is resolved
- THEN decision is `deny`

#### Scenario: Approve when no blockers
- GIVEN no escalate-level or deny-level signals
- WHEN final decision is resolved
- THEN decision is `approve`

### Requirement: Tool Failure Transparency
The agent SHALL catch tool errors, continue decision resolution with available signals, and
include failure details in `rationale`.

#### Scenario: Tool exception occurs
- GIVEN one tool raises an exception during a recommendation run
- WHEN the agent handles the request
- THEN the agent does not crash
- AND the final rationale includes the failed tool and error summary
- AND the final decision is `escalate`
