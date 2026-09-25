"""Build submission artifacts from benchmark_outputs/*.json."""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "benchmark_outputs")
SUB  = os.path.join(ROOT, "submission")
os.makedirs(SUB, exist_ok=True)

cases = sorted(glob.glob(os.path.join(OUT, "HHG-*.json")))
all_cases = []

for path in cases:
    with open(path, "r", encoding="utf-8") as f:
        r = json.load(f)

    cid     = r.get("case_id")
    cust    = r.get("customer_id")
    inv     = r.get("investigation", {}) or {}
    assess  = r.get("assessment", {}) or {}
    mem     = r.get("memory", {}) or {}
    dec     = r.get("decision", {}) or {}
    bench   = r.get("benchmark_input", {}) or {}

    requires_sar = (
        assess.get("risk_level") in ("very_high", "high")
        and dec.get("recommended_action") not in ("allow_transaction", "monitor")
    )

    lines = []
    lines.append(f"# Case {cid}\n")
    lines.append(f"- **Customer:** `{cust}`")
    lines.append(f"- **Trigger:** {bench.get('trigger_type')} — {bench.get('trigger_text')}")
    lines.append(f"- **Flagged txn:** `{bench.get('flagged_txn_id')}`")
    lines.append(f"- **Risk level:** **{assess.get('risk_level')}** (score {assess.get('risk_score')})")
    lines.append(f"- **Recommended action:** `{dec.get('recommended_action')}`")
    lines.append(f"- **Approval route:** `{dec.get('approval_route') or 'n/a'}`")
    lines.append(f"- **SAR required:** {'yes' if requires_sar else 'no'}\n")

    lines.append("## Evidence\n")
    for e in inv.get("evidence", []):
        lines.append(f"- **{e.get('type')}** ({e.get('severity')}): {e.get('description')}")
    lines.append("")

    lines.append("## Findings\n")
    for fnd in inv.get("findings", []):
        if isinstance(fnd, dict):
            lines.append(f"- **{fnd.get('type') or fnd.get('name')}** — {fnd.get('description') or ''}")
        else:
            lines.append(f"- {fnd}")
    lines.append("")

    lines.append("## Assessment\n")
    lines.append(f"- risk_level: `{assess.get('risk_level')}`")
    lines.append(f"- risk_score: `{assess.get('risk_score')}`")
    for k in ("supporting_evidence", "uncertainty", "fraud_patterns", "hypotheses"):
        if assess.get(k):
            lines.append(f"- {k}: {json.dumps(assess[k], default=str)[:400]}")
    lines.append("")

    lines.append("## Historical Memory\n")
    matches = mem.get("matches") or mem.get("similar_cases") or []
    lines.append(f"- {len(matches)} similar historical case(s) retrieved")
    for m in matches[:5]:
        lines.append(f"  - `{m.get('case_id') or m.get('id')}` — {m.get('pattern') or m.get('outcome') or ''}")
    lines.append("")

    lines.append("## Recommended Action & Approval\n")
    lines.append(f"- action: `{dec.get('recommended_action')}`")
    lines.append(f"- reason: {dec.get('reason') or dec.get('rationale') or ''}")
    lines.append(f"- approval_route: `{dec.get('approval_route') or 'n/a'}`")
    lines.append(f"- policy: `{dec.get('policy') or 'n/a'}`")
    lines.append("")

    if requires_sar:
        lines.append("## Suspicious Activity Report (draft)\n")
        lines.append(f"SAR for customer `{cust}` — case `{cid}`. "
                     f"Risk level: {assess.get('risk_level')} "
                     f"(score {assess.get('risk_score')}). "
                     f"Recommended action: {dec.get('recommended_action')}.")
        lines.append("")

    with open(os.path.join(SUB, f"{cid}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    all_cases.append({
        "case_id": cid,
        "customer_id": cust,
        "benchmark_input": bench,
        "risk_level": assess.get("risk_level"),
        "risk_score": assess.get("risk_score"),
        "recommended_action": dec.get("recommended_action"),
        "approval_route": dec.get("approval_route"),
        "sar_required": requires_sar,
        "evidence_count": len(inv.get("evidence", [])),
        "finding_count": len(inv.get("findings", [])),
        "historical_matches": len(matches),
        "full_record": r,
    })

with open(os.path.join(SUB, "all_cases.json"), "w", encoding="utf-8") as f:
    json.dump(all_cases, f, indent=2, default=str)

print(f"Wrote {len(cases)} case files + all_cases.json to {SUB}")