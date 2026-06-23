# Capability: Data Loader Access

## ADDED Requirements

### Requirement: Loader-only Access to Mock Data
The system SHALL load mock procurement data through functions in `data/loader.py` and SHALL NOT
read files from `mock_data/` directly in tool or agent code.

#### Scenario: Tool retrieves budgets through loader
- GIVEN a tool execution requiring budget data
- WHEN the tool reads data
- THEN the tool calls a function from `data/loader.py`
- AND no direct JSON file read is performed in tool code

#### Scenario: Agent does not bypass loader
- GIVEN an agent recommendation run
- WHEN supporting data is required
- THEN data access occurs through tool calls that use loader functions

### Requirement: Stable Loader Interfaces
The system SHALL provide loader functions for budgets, vendors, policies, and requests that return
typed Python structures suitable for tool evaluation.

#### Scenario: Retrieve all required datasets
- GIVEN the mock dataset is present
- WHEN loader functions are called
- THEN budgets, vendors, policies, and requests are each retrievable without direct caller file I/O
