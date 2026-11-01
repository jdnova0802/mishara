# Clean-provenance SKU (RealPage family) — scoping only

**Status:** second SKU, same DENY family. Not outbound-ready as a sold weld yet.  
**Question:** prove, independently and continuously, that a pricing algorithm’s recommendation never used forbidden competitor data.  
**Not the same as write-stop:** write-stop = “halted in time.” Clean provenance = “trained/served only on allowed inputs.”

## Regulatory grounding (real)
- **DOJ v. RealPage** proposed final judgment / settlement (filed ~Nov 24, 2025): cease using competitors’ nonpublic competitively sensitive data in **runtime operation**; model training limited to aged (≥12 months) backward-looking data not from active leases; geographic effect caps; no market surveys / strategy forums that share CSI; monitor.  
  Sources: DOJ OPA release; Proposed Final Judgment; Competitive Impact Statement.
- **NY Donnelly Act** amendment track + **EC / Poland** algorithmic pricing / housing investigations — same family: shared nonpublic inputs → coordinated outcomes.
- Product gap: decree text is a **prohibition**. There is still almost no **stranger-checkable continuous proof** that a live recommendation complied.

## DENY family (same architecture, different claim)
| | Write-stop (Gate today) | Clean provenance (this SKU) |
|--|--|--|
| Moment | Before irreversible act | Before / at recommendation emit |
| Failure mode | Cap breach, routing anomaly, injection | Forbidden feature/input used |
| Receipt says | GO/NO_GO/HOLD on act | CLEAN / TAINTED / UNKNOWN on feature vector |
| Buyer pain | Agent paid / bound / pushed | Landlord / RMS vendor facing decree / discovery |

## Receipt schema (variant of existing, not a fork of crypto)
Propose `gate-clean-provenance-v1` as a **claim_scope** variant on the same signed JWT mouth:

```json
{
  "spec": "gate-clean-provenance-v1",
  "jti": "cp_…",
  "dec": "CLEAN | TAINTED | UNKNOWN",
  "fp": "<hash of recommendation + model_id + input_manifest>",
  "scope": {
    "as_of": "ISO-8601",
    "product_id": "rms_airm_v…",
    "property_id": "…",
    "runtime_forbidden_inputs": ["unaffiliated_property_csi", "active_lease_peer"],
    "training_policy": {
      "min_age_days": 365,
      "active_leases_excluded": true,
      "geo_granularity_max": "statewide"
    },
    "attested_inputs": ["own_property_series", "public_cpi", "aged_peer_12m"],
    "monitor_epoch": "…"
  },
  "sig": ["forbidden_input_absent", "training_age_ok"]
}
```

**Fields that must be stranger-checkable (or explicitly UNKNOWN):**
1. Model / product id + version hash  
2. Input manifest hash (what features entered runtime)  
3. Policy epoch (which decree/contract version)  
4. Decision CLEAN/TAINTED/UNKNOWN  
5. Time of recommendation  

Fail closed: missing manifest → UNKNOWN or TAINTED, never silent CLEAN.

## Mouth vs endpoint
**Recommendation: new receipt type on the existing prefinality / claim_scope architecture, exposed as a separate mouth route** — same signing keys, same stranger verify, different evaluate policy.

| Option | Verdict |
|--------|---------|
| Stuff into `/v1/prefinality/evaluate` as another `rail` | Possible (`rail: provenance`) but conflates act-clearance with input-clearance |
| Separate mouth `/v1/provenance/evaluate` + `/.well-known/provenance.json` | **Preferred** — buyers understand “different question, same Gate” |
| Totally separate product | Overkill; loses receipt verify + family scorecard |

## First buyers (not outbound this pass)
1. RMS / revenue-management vendors under consent-decree pressure  
2. Large PM companies that must show continuous compliance to a monitor  
3. Insurers / lenders asking “was this rent set with peer CSI?” in diligence  

## What is *not* claimed
- That Gate replaces the court-appointed monitor  
- That CLEAN means antitrust-safe forever  
- That vendors must stream raw competitor data to Nisaba (they must not)

## Next build slice (when greenlit)
1. `claim_scope` helper for provenance decisions  
2. Dogfood `/demo/provenance/evaluate` with fixture input manifests  
3. One PDF one-pager mapping decree ¶IV prohibitions → receipt signals  
