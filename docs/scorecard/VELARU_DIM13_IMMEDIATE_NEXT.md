# IMMEDIATE NEXT — Velaru Dim 13 (not a someday)

Status: **blocking portfolio close of Dim 13**. Gate/Mishara Dim 13 is closed in CI; Velaru is not.

## 1. Set the secret (this PR / today)

Repo: `jdnova0802/mishara` → Settings → Secrets and variables → Actions

| Name | Value |
|---|---|
| `VELARU_GITHUB_TOKEN` | PAT with read access to `jdnova0802/velaru` (same credential already available to Cloud Agents as env `VELARU_GITHUB_TOKEN`) |

Without this secret, job `velaru-surface` in `.github/workflows/zero-tolerance-gates.yml` **fails on purpose**. An optional scan that never runs is the same failure mode as a manifest referencing a page that never gets built.

## 2. Land Velaru route deletion

Branch (already pushed): `cursor/drop-legacy-dtcc-routes-25ad`  
Open PR from: https://github.com/jdnova0802/velaru/pull/new/cursor/drop-legacy-dtcc-routes-25ad

Removes `/dtcc`, `/foundry/dtcc`, and all `/api/v1/dtcc/*` (including 302/308 redirects). Tests expect **404**.

After merge to Velaru `main`, flip the mishara workflow `ref:` from that branch to `main`.

## 3. Live prove (after Velaru deploy)

```bash
curl -sI https://velaru.xyz/dtcc | head -1          # expect 404
curl -sI https://velaru.xyz/api/v1/dtcc/attest | head -1  # expect 404
```

## Explicitly later (not this ticket)

Full DTCC **word** purge across Velaru module names / sales docs — separate from the path floor (`--velaru-routes-only`).
