# PASTE TO CLAUDE — DSP Reject mouth just shipped

Branch: `cursor/dsp-reject-mouth-ce84`

## What
Apple mouth for **28 CFR § 202.1104** (DOJ Data Security Program):

Affirmative reject (incl. automated) of a prohibited **data-brokerage** offer involving bulk U.S. sensitive / government-related data with a covered person / country of concern, on/after **Oct 6, 2025** → **REPORT DUE** to NSD within **14 days**.

Gate **classifies + packs**. Gate **never files**.

## Surface
- Page: `/dsp-reject`
- API: `POST /v1/dsp-reject`
- Manifest: `/.well-known/dsp-reject.json`
- Words: `REPORT DUE` | `NOT THIS` | `HOLD`

## On REPORT DUE
- `report_pack` with § 202.1104(c) fields + `mailto:NSD.FIRS.datasecurity@usdoj.gov`
- `write_state.phase = IN_FLIGHT` (14-day clock; not cancellable)
- Signed `claim_scope` (Covered Persons List explicitly non-exhaustive)

## Primary
- https://www.ecfr.gov/current/title-28/chapter-I/part-202/subpart-K/section-202.1104
- 90 Fed. Reg. 1636 (Jan 8, 2025)
- DOJ Compliance Guide Apr 11, 2025

## Not
Monday diligence cash. Event rate unknown. Dogfoodable theory-floor mouth outside insurance/payments.
