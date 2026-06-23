# Capability: Risk Assessment Tool

## ADDED Requirements

### Requirement: Vendor Risk Profile Retrieval
The system SHALL provide `assess_risk(vendor_id)` that returns a vendor risk profile including
compliance flag status, contract status, and a computed risk level.

#### Scenario: Return risk profile for known vendor
- GIVEN a `vendor_id` present in vendor data
- WHEN `assess_risk` runs
- THEN response includes `vendor_id`
- AND response includes `compliance_flag_status`
- AND response includes `contract_status`
- AND response includes `risk_level`

### Requirement: Risk Level Enumeration
The computed `risk_level` SHALL be constrained to one of: `low`, `medium`, `high`, `critical`.

#### Scenario: Valid risk level value returned
- GIVEN any successful risk assessment
- WHEN `assess_risk` returns
- THEN `risk_level` is one of `low | medium | high | critical`

#### Scenario: Invalid risk level is rejected
- GIVEN an internal attempt to return `risk_level = severe`
- WHEN output validation is applied
- THEN validation fails

### Requirement: Deterministic Risk Computation Inputs
Risk computation SHALL be derived from at least compliance flag status and contract status.

#### Scenario: Compliance-flagged vendor maps to elevated risk
- GIVEN vendor record has active compliance flag
- WHEN `assess_risk` computes risk level
- THEN resulting `risk_level` is `high` or `critical`

#### Scenario: Expired contract maps to elevated risk
- GIVEN vendor record has `contract_status = expired`
- WHEN `assess_risk` computes risk level
- THEN resulting `risk_level` is `high` or `critical`

### Requirement: Unknown Vendor Handling
The tool SHALL handle unknown vendor IDs as a non-silent failure path.

#### Scenario: Unknown vendor escalates
- GIVEN `vendor_id` does not exist in vendor data
- WHEN `assess_risk` runs
- THEN response signals `escalate`-equivalent handling for agent orchestration
- AND rationale or error details indicate vendor was not found
