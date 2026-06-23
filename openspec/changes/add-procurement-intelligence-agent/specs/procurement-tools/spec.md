# Capability: Procurement Check Tools

## ADDED Requirements

### Requirement: Budget Check Tool
The system SHALL provide a `check_budget` tool that evaluates whether the request amount can be
covered by the relevant budget context.

#### Scenario: Budget supports request
- GIVEN a request with amount within available budget
- WHEN `check_budget` runs
- THEN it reports a pass result with explanatory detail

#### Scenario: Budget does not support request
- GIVEN a request with amount exceeding available budget
- WHEN `check_budget` runs
- THEN it reports a deny-level result with explanatory detail

### Requirement: Vendor Duplication Check Tool
The system SHALL provide a `check_vendor_duplication` tool that identifies duplicate vendor or
duplicate-request conditions according to mock data.

#### Scenario: Duplicate risk is detected
- GIVEN a request matching an existing duplicate condition
- WHEN `check_vendor_duplication` runs
- THEN it reports a deny-level or escalate-level signal with detail

### Requirement: Policy Compliance Check Tool
The system SHALL provide a `check_policy_compliance` tool that validates the request against
applicable procurement policies.

#### Scenario: Policy violation is detected
- GIVEN a request violating one or more active policies
- WHEN `check_policy_compliance` runs
- THEN it reports a deny-level result listing violated policy context

### Requirement: Risk Assessment Tool
The system SHALL provide an `assess_risk` tool that determines request risk posture and flags
high-risk or uncertain conditions.

#### Scenario: High-risk request is detected
- GIVEN a request with high-risk indicators
- WHEN `assess_risk` runs
- THEN it reports an escalate-level result with risk rationale

### Requirement: Tool Function Documentation
Each public tool function SHALL include a docstring describing purpose, expected inputs, and
result semantics so the agent can reliably invoke the correct tool.

#### Scenario: Tool has usable docstring
- GIVEN any public tool function
- WHEN inspected by developers or agent orchestration code
- THEN the docstring describes what the check evaluates and how to interpret its outcome
