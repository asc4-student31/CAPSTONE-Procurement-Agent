# Capability: Models and Output Contract

## ADDED Requirements

### Requirement: Validated Purchase Request Input Model
The system SHALL define a Pydantic v2 `PurchaseRequest` model used as the canonical request input
contract for procurement pre-screening.

#### Scenario: Accept valid request payload
- GIVEN a request payload containing all required fields with valid types
- WHEN the payload is validated as `PurchaseRequest`
- THEN model validation succeeds

#### Scenario: Reject invalid request payload
- GIVEN a request payload with missing required fields or invalid types
- WHEN the payload is validated as `PurchaseRequest`
- THEN model validation fails with explicit field errors

### Requirement: Structured Recommendation Output Model
The system SHALL define a Pydantic v2 `ProcurementRecommendation` model with fields `decision`
and `rationale`.

#### Scenario: Allow approved decision values only
- GIVEN a recommendation with `decision` value `approve`, `deny`, or `escalate`
- WHEN validated as `ProcurementRecommendation`
- THEN model validation succeeds

#### Scenario: Reject out-of-contract decision values
- GIVEN a recommendation with `decision` value outside `approve`, `deny`, `escalate`
- WHEN validated as `ProcurementRecommendation`
- THEN model validation fails

### Requirement: Non-empty Rationale
The system SHALL require `ProcurementRecommendation.rationale` to be non-empty after trimming
whitespace.

#### Scenario: Reject empty rationale
- GIVEN a recommendation where rationale is empty or only whitespace
- WHEN validated as `ProcurementRecommendation`
- THEN model validation fails
