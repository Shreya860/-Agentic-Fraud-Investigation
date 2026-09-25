# Case CASE-001

- **Customer:** `C12382`
- **Trigger:** risk_score — Real-time model scored transaction 3514030 ($77.07, in billing region 444.0) at 0.61. Review and decide.
- **Flagged txn:** `3514030`
- **Risk level:** **high** (score 0.84)
- **Recommended action:** `request_customer_validation`
- **Approval route:** `authorized_analyst`
- **SAR required:** yes

## Evidence

- **transaction_history** (informational): Customer has 422 recorded transactions.
- **high_risk_transactions** (high): 1 recent/high-risk transactions were identified, with maximum risk score 0.84.
- **shared_card_network** (informational): No other customers were connected through a sufficiently complete shared card key.
- **shared_device_network** (suspicious): 50 customer connections were found through device fingerprints that are not among the common generic fingerprints.
- **email_domains** (informational): Customer is associated with 10 email domains.
- **transaction_channels** (informational): Observed transaction channels were in_person, online.

## Findings

- **None** — The customer has transaction activity with a risk score of at least 0.80.

## Assessment

- risk_level: `high`
- risk_score: `0.84`
- supporting_evidence: [{"type": "high_risk_transactions", "severity": "high", "description": "1 recent/high-risk transactions were identified, with maximum risk score 0.84."}]
- uncertainty: ["No shared-card customer connection was identified.", "Customer validation evidence is not currently available.", "Step-up authentication evidence is not currently available.", "External fraud intelligence is not currently available.", "Historical case similarity was evaluated; 4 matching historical case(s) were found."]
- fraud_patterns: [{"pattern": "high_risk_transaction_activity", "confidence": "medium", "reason": "The customer has transaction activity with elevated risk scores."}]

## Historical Memory

- 0 similar historical case(s) retrieved

## Recommended Action & Approval

- action: `request_customer_validation`
- reason: Important transaction-risk evidence is available, but customer validation is still missing.
- approval_route: `authorized_analyst`
- policy: `{'action': 'request_customer_validation', 'allowed': True, 'requires_approval': True, 'approval_route': 'authorized_analyst', 'category': 'evidence_gathering', 'status': 'awaiting_approval', 'reason': "Action 'request_customer_validation' is allowed but requires approval from authorized_analyst."}`

## Suspicious Activity Report (draft)

SAR for customer `C12382` — case `CASE-001`.
Basis: risk level high (score 0.84) supported by 6 evidence item(s) and 1 finding(s).
Recommended action: request_customer_validation.
