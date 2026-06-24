# Capability: Procurement Agent

## ADDED Requirements

### Requirement: Typed Input and Output Contract
The system SHALL provide an `agent.py` orchestration entrypoint that accepts `PurchaseRequest`
from `models.py` and returns `ProcurementRecommendation` from `models.py`.

#### Scenario: Valid input produces typed recommendation
- GIVEN a valid `PurchaseRequest`
- WHEN the procurement agent evaluates the request
- THEN the returned object validates as `ProcurementRecommendation`

#### Scenario: Output decision and rationale constraints are preserved
- GIVEN any successful agent evaluation
- WHEN output validation is applied
- THEN `decision` is one of `approve | deny | escalate`
- AND `rationale` is a non-empty string

### Requirement: Agent Uses Four Screening Tools
The agent SHALL execute or attempt all four screening tools for every evaluated request:
`check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk`.

#### Scenario: Complete tool coverage per request
- GIVEN one purchase request
- WHEN the agent runs
- THEN `check_budget` is called with budget fields from the request
- AND `check_vendor_duplication` is called with vendor/category/amount fields
- AND `check_policy_compliance` is called with the full `PurchaseRequest`
- AND `assess_risk` is called with `vendor_id`

#### Scenario: Partial tool failure still preserves workflow completeness
- GIVEN one tool raises during execution
- WHEN the agent runs remaining checks
- THEN the other three tools are still executed or attempted

### Requirement: Decision Priority Is Deterministic
The agent SHALL resolve final recommendation priority with strict order:
`escalate > deny > approve`.

#### Scenario: Escalate has highest priority
- GIVEN tool outcomes include at least one escalate signal and any deny/approve-compatible signals
- WHEN final decision is resolved
- THEN final `decision` is `escalate`

#### Scenario: Deny is selected when no escalate exists
- GIVEN tool outcomes include one or more deny signals and no escalate signals
- WHEN final decision is resolved
- THEN final `decision` is `deny`

#### Scenario: Approve only when no higher-severity signals exist
- GIVEN all tool outcomes are approve-compatible
- WHEN final decision is resolved
- THEN final `decision` is `approve`

### Requirement: Tool and Orchestration Errors Are Surfaced
The agent SHALL catch tool exceptions and include failure details in the recommendation rationale
rather than failing silently or crashing the workflow.

#### Scenario: Single tool exception yields error-aware recommendation
- GIVEN one screening tool raises an exception
- WHEN the agent completes evaluation
- THEN the agent still returns `ProcurementRecommendation`
- AND `rationale` contains non-empty text describing the tool failure

#### Scenario: Multiple failures still return structured output
- GIVEN multiple tool calls fail
- WHEN the agent resolves final recommendation
- THEN final output remains schema-valid
- AND failure context is included in rationale

### Requirement: System Prompt Enforces Operational Constraints
The system prompt in `agent.py` SHALL constrain model behavior to mandatory workflow and output
rules for procurement decisions.

#### Scenario: Prompt enforces mandatory tool usage
- GIVEN the agent receives a request to evaluate
- WHEN the model follows system instructions
- THEN instructions require running or attempting all four tools before final recommendation

#### Scenario: Prompt enforces policy-aware rationale quality
- GIVEN tool outputs are available
- WHEN the model drafts rationale
- THEN rationale references key findings from budget, policy, vendor-duplication, and risk checks
- AND rationale includes error details when failures occur

#### Scenario: Prompt enforces no out-of-contract decisions
- GIVEN the model proposes a recommendation
- WHEN output is generated
- THEN prompt constraints prohibit decision labels outside `approve | deny | escalate`
