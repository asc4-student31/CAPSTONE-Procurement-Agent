# Vendor Policy Triggers

## Compliance Flag Trigger (POL-006 -> escalate)
- Vendor: Vertex Consulting Group
- Vendor ID: V-006
- Evidence: compliance_flag is true in mock_data/vendors.json.

## Expired Contract Trigger (POL-005 -> deny)
- Vendor: Crestview Print and Media
- Vendor ID: V-010
- Evidence: contract_status is expired in mock_data/vendors.json.

## Office Supplies Duplication Trigger (active contracts in same category)
- Vendor 1: Apex Office Supplies (V-001)
- Vendor 2: Meridian Office Products (V-003)
- Category: office_supplies
- Evidence: both vendors are in office_supplies and both have contract_status active in mock_data/vendors.json.
