# Policy Decision Matrix

Source: [mock_data/policies.json](mock_data/policies.json)

| Policy | Trigger condition | Forced decision | Amount threshold applies? |
|---|---|---|---|
| POL-001 Single-Source Restriction | Request is in an affected category, amount is over $25,000, and vendor is not the contracted active vendor for that category. | deny | Yes. Greater than $25,000. |
| POL-002 Manager Approval Threshold | Request amount is between $10,000 and $49,999.99 and manager approval is missing. | non-compliant process state (typically escalate for approval) | Yes. $10,000 to $49,999.99. |
| POL-003 Director Approval Threshold | Request amount is $50,000 or more and director approval is missing. | escalate | Yes. Greater than or equal to $50,000. |
| POL-004 Prohibited Category - Catering | Category is catering/food service under the spend reduction rule. | deny | No. Applies regardless of amount. |
| POL-005 Expired Contract Vendor | Vendor contract is expired. | deny | No. |
| POL-006 Compliance-Flagged Vendor Hold | Vendor has an active compliance flag. | escalate | No. |
| POL-007 Staffing Vendor Single-Source | Staffing engagement uses a non-contracted staffing vendor and exceeds 40 hours. | deny | Yes. Greater than 40 hours (engagement duration threshold). |
| POL-008 Budget Overage Prohibition | Request would exceed remaining quarterly budget for the cost center. | deny | No fixed dollar threshold; budget-limit dependent. |

## Notes

- POL-002 does not explicitly say deny or escalate in the policy text; it marks missing approval as non-compliant.
- For implementation consistency, treat POL-002 as an escalation/workflow gate unless your OpenSpec defines a different forced decision.
