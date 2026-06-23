# requests.json Brief

This dataset contains 15 procurement test cases in mock_data/requests.json.
Each case includes a labeled decision in expected_outcome and a human-readable rationale in outcome_reason.
Primary labels are approve, deny, and escalate. One case (REQ-015) is intentionally marked ambiguous as an edge-case test.

## Expected Outcomes and Reasons by Test Case

| Request ID | expected_outcome | outcome_reason |
|---|---|---|
| REQ-001 | approve | Active contract with BlueSky exists for software_licenses. Amount is within CC-001 remaining budget of $187,550. Below director threshold. No policy violations. |
| REQ-002 | approve | Active contract with Pinnacle Hardware for hardware. Amount is within CC-004 remaining budget of $210,800. Requires manager approval (POL-002) but that is a process note, not a denial trigger. No violations. |
| REQ-003 | approve | Active contract with Skyline. Amount is well within CC-006 remaining budget of $348,700. Below manager approval threshold. No violations. |
| REQ-004 | approve | Active contract with Delta Fleet Parts. Amount within CC-008 budget of $83,600. Just below the manager approval threshold. No violations. |
| REQ-005 | approve | Active contract with Ironclad. Amount within CC-001 budget. Manager approval range but no violation. Contracted vendor for category. |
| REQ-006 | deny | CC-003 has only $6,900 remaining. This request would exceed the quarterly budget by $4,300. POL-008 prohibits budget overage approvals. |
| REQ-007 | deny | Crestview Print and Media has an expired contract (CTR-2023-0077 expired 2025-09-30). POL-005 prohibits purchases from expired-contract vendors until renewal is complete. |
| REQ-008 | deny | NovaPrint has no active contract. Two vendors (Apex Office Supplies V-001 and Meridian Office Products V-003) hold active contracts for office_supplies. Amount exceeds POL-001 threshold of $25,000, making this a single-source restriction violation. |
| REQ-009 | deny | POL-004 prohibits all catering purchases under the Q4 2025 corporate spend reduction initiative. Denied regardless of amount or budget availability. |
| REQ-010 | escalate | Active contract with Delta Fleet Parts. CC-009 has $37,900 remaining - this request of $49,600 exceeds the available budget. Also crosses the director approval threshold (POL-003: $50,000+) within 1% of trigger. Budget overage and near-threshold amount both warrant escalation for director review rather than outright denial. |
| REQ-011 | escalate | Vertex Consulting Group has an active compliance flag (pending ethics review since 2025-11-03). POL-006 requires all purchases from compliance-flagged vendors to be escalated to Legal and Compliance before approval. |
| REQ-012 | approve | Active enterprise staffing contract with Globalink. Amount within CC-002 remaining budget of $51,250. Below manager threshold. Correct contracted vendor for staffing category. |
| REQ-013 | approve | No active contract required for training category (no single-source policy applies). Amount within CC-007 remaining budget of $18,000. Manager approval range but no policy violation. |
| REQ-014 | escalate | Orion Data Systems holds an active hardware contract and amount is within CC-006 budget. However, amount is $47,500 - within 5% of the $50,000 director approval threshold (POL-003). Near-threshold escalation is warranted to ensure director is aware before commitment. |
| REQ-015 | ambiguous | FastTrack has no active contract but courier_services has no single-source restriction policy and no competing contracted vendor. CC-005 has only $5,500 remaining - amount is within budget. No category prohibition. Outcome depends on system prompt design: a conservative agent may escalate given the tight budget position; a permissive agent may approve given no policy violation. This is the ambiguous test case. |
