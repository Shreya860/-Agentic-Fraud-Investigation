# Case CASE-015

- **Customer:** `C03042`
- **Trigger:** risk_score — Real-time model scored transaction 3464869 ($599.94, online) at 0.77. Review and decide.
- **Flagged txn:** `3464869`
- **Risk level:** **high** (score 0.87)
- **Recommended action:** `request_customer_validation`
- **Approval route:** `authorized_analyst`
- **SAR required:** yes

## Evidence

- **transaction_history** (informational): Customer has 79 recorded transactions.
- **high_risk_transactions** (high): 2 recent/high-risk transactions were identified, with maximum risk score 0.87.
- **shared_card_network** (informational): No other customers were connected through a sufficiently complete shared card key.
- **shared_device_network** (suspicious): 17 customer connections were found through device fingerprints that are not among the common generic fingerprints.
- **rare_device_fingerprint** (suspicious): 1 relatively rare device fingerprints were identified.
- **email_domains** (informational): Customer is associated with 13 email domains.
- **transaction_channels** (informational): Observed transaction channels were in_person, online.

## Findings

- **None** — The customer has transaction activity with a risk score of at least 0.80.
- **None** — The customer uses one or more relatively rare device fingerprints.
- **None** — Some customer connections use common device fingerprints. These connections should not be treated as strong evidence without additional corroborating signals.

## Assessment

- risk_level: `high`
- risk_score: `0.87`
- supporting_evidence: [{"type": "high_risk_transactions", "severity": "high", "description": "2 recent/high-risk transactions were identified, with maximum risk score 0.87."}, {"type": "rare_device_fingerprint", "severity": "suspicious", "description": "1 relatively rare device fingerprints were identified."}]
- uncertainty: ["No shared-card customer connection was identified.", "Customer validation evidence is not currently available.", "Step-up authentication evidence is not currently available.", "External fraud intelligence is not currently available.", "Historical case similarity was evaluated; 6 matching historical case(s) were found."]
- fraud_patterns: [{"pattern": "high_risk_transaction_activity", "confidence": "medium", "reason": "The customer has transaction activity with elevated risk scores."}, {"pattern": "rare_device_fingerprint", "confidence": "low", "reason": "The customer is associated with relatively rare device fingerprints."}]

## Historical Memory

- 0 similar historical case(s) retrieved

## Recommended Action & Approval

- action: `request_customer_validation`
- reason: Important transaction-risk evidence is available, but customer validation is still missing.
- approval_route: `authorized_analyst`
- policy: `{'action': 'request_customer_validation', 'allowed': True, 'requires_approval': True, 'approval_route': 'authorized_analyst', 'category': 'evidence_gathering', 'status': 'awaiting_approval', 'reason': "Action 'request_customer_validation' is allowed but requires approval from authorized_analyst."}`

## Suspicious Activity Report (draft)

SAR for customer `C03042` — case `CASE-015`.
Basis: risk level high (score 0.87) supported by 7 evidence item(s) and 3 finding(s).
Recommended action: request_customer_validation.
