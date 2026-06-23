# Capability: Vendor Duplication Tool

## ADDED Requirements

### Requirement: Category Contract Conflict Detection
The system SHALL provide `check_vendor_duplication(vendor_id, purchase_category, amount)` to
identify active-contract conflicts where another vendor already holds an active contract in the
same category.

#### Scenario: Active conflicting vendor exists
- GIVEN a request for vendor `Vx` in category `C`
- AND at least one different vendor has `contract_status = active` in category `C`
- WHEN `check_vendor_duplication` runs
- THEN the response includes a non-empty `conflicting_vendor_ids` list
- AND the response includes `contract_details` for each conflicting vendor

#### Scenario: No active conflicting vendor exists
- GIVEN a request for vendor `Vx` in category `C`
- AND no different vendor has `contract_status = active` in category `C`
- WHEN `check_vendor_duplication` runs
- THEN `conflicting_vendor_ids` is empty
- AND `contract_details` is empty

### Requirement: POL-001 Deny Trigger Integration
The tool SHALL reference policy `POL-001` threshold amount semantics for decision forcing.

#### Scenario: Conflict above POL-001 threshold forces deny
- GIVEN one or more active conflicting vendors in the same category
- AND request amount is strictly greater than `POL-001.threshold_amount`
- WHEN `check_vendor_duplication` evaluates outcome
- THEN `forced_decision` is `deny`
- AND rationale references `POL-001`

#### Scenario: Conflict at or below POL-001 threshold does not auto-deny
- GIVEN one or more active conflicting vendors in the same category
- AND request amount is less than or equal to `POL-001.threshold_amount`
- WHEN `check_vendor_duplication` evaluates outcome
- THEN `forced_decision` is `escalate` or equivalent non-deny review signal
- AND rationale references threshold handling

### Requirement: Conflict Detail Shape
Each conflict detail SHALL include enough contract context for downstream rationale generation.

#### Scenario: Contract detail fields returned
- GIVEN an identified conflicting vendor
- WHEN `check_vendor_duplication` returns details
- THEN each detail entry includes at least `vendor_id`, `contract_id`, `contract_status`, and `category`
