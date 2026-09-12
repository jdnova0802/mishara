# Core Web Vitals / Lighthouse baselines

**Measured:** 2026-09-12 (UTC) via Lighthouse 12 headless Chrome against live hosts.

| Surface | Perf | A11y | LCP | CLS |
|---------|------|------|-----|-----|
| `https://gate.velaru.xyz/` | 1.00 | 0.85→retest after muted/link CSS | 0.9s | 0 |
| `https://gate.velaru.xyz/pricing` | 1.00 | 0.84 | 0.8s | — |
| `https://gate.velaru.xyz/bind-room` | 1.00 | 0.88 | 0.9s | — |
| `https://mishara.onrender.com/` | 0.99 | 1.00 | 1.6s | — |

Artifacts: `*.report.json` (+ Gate home HTML) in this folder.

**Follow-up:** after Gate CSS contrast/underline deploy, re-run Gate a11y; target ≥0.95.
