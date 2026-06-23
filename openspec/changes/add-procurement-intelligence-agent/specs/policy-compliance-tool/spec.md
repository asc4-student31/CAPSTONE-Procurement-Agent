# Capability: Policy Compliance Tool

## ADDED Requirements

### Requirement: Full Policy Set Evaluation
The system SHALL provide `check_policy_compliance(purchase_request)` that evaluates the request
against all 8 policy records from `mock_data/policies.json` through `data/loader.py`.

#### Scenario: Evaluate all eight policies
- GIVEN a valid purchase request
- WHEN `check_policy_compliance` runs
- THEN each of the eight policy definitions is evaluated
- AND no policy is skipped silently

### Requirement: Policy Violation Reporting
The tool SHALL return a list of policy violations when non-compliance is detected.

#### Scenario: Return empty violations for compliant request
- GIVEN a request that violates no policy
- WHEN `check_policy_compliance` runs
- THEN `violations` is an empty list

#### Scenario: Return one or more violation entries
- GIVEN a request that violates one or more policies
- WHEN `check_policy_compliance` runs
- THEN `violations` contains one entry per violated policy

### Requirement: Violation Entry Contract
Each violation entry SHALL include `policy_id`, `violated_rule`, and `forced_decision` where
`forced_decision` is constrained to `deny` or `escalate`.

#### Scenario: Violation shape is complete
- GIVEN any violated policy
- WHEN a violation entry is returned
- THEN `policy_id` matches a known policy identifier
- AND `violated_rule` contains the specific rule text or resolved rule summary
- AND `forced_decision` is either `deny` or `escalate`

#### Scenario: Invalid forced decision is rejected
- GIVEN an internal attempt to produce a violation with `forced_decision = approve`
- WHEN output validation is applied
- THEN validation fails for that violation entry

### Requirement: Deterministic Multi-violation Outcome Signal
The tool SHALL surface an aggregate outcome based on returned violations.

#### Scenario: Any escalate violation yields escalate aggregate
- GIVEN violations include at least one `forced_decision = escalate`
- WHEN aggregate tool outcome is resolved
- THEN aggregate outcome is `escalate`

#### Scenario: Deny-only violations yield deny aggregate
- GIVEN violations are non-empty and all have `forced_decision = deny`
- WHEN aggregate tool outcome is resolved
- THEN aggregate outcome is `deny`
