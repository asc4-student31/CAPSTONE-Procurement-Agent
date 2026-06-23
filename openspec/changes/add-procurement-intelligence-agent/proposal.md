# Change Proposal: add-procurement-intelligence-agent

## Why
Procurement analysts spend significant time manually pre-screening straightforward purchase requests.
A consistent pre-screening agent can reduce analyst workload while preserving human decision authority.
The current repository has only scaffolding in the root package and does not yet define a required
capability for structured procurement recommendations.

## What Changes
This proposal adds a Pydantic AI procurement intelligence capability that:
- accepts a `PurchaseRequest` input model and returns a `ProcurementRecommendation` output model
- constrains recommendation decision values to `approve`, `deny`, or `escalate`
- requires every recommendation to include a non-empty rationale
- reads all mock reference data via `data/loader.py` only
- invokes and combines four tools in `tools/`: `check_budget`, `check_vendor_duplication`,
  `check_policy_compliance`, and `assess_risk`
- applies deterministic final decision priority: `escalate` > `deny` > `approve`
- catches tool errors and includes them in the final rationale rather than failing silently

## Scope
In scope:
- Pydantic v2 model contracts for request input and recommendation output
- data loader interfaces used by tool implementations
- tool behavior contracts for budget, duplication, policy, and risk checks
- agent orchestration behavior and decision resolution policy

Out of scope:
- edits to files under `mock_data/`
- replacing the advisory human-in-the-loop procurement decision process
- live API integrations outside provided mock data fixtures

## Impact
Expected impact:
- Enables implementation and verification of all three decision outcomes (`approve`, `deny`, `escalate`)
- Establishes predictable, testable behavior for procurement pre-screening
- Improves error transparency by surfacing tool failures in rationale text
- Provides spec coverage for models, tools, data access, and agent wiring
