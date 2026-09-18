# @gate/right-to-act

Fail-closed **Right-to-Act** before an irreversible sink runs.

Invariant: **Computation does not confer authority for consequence.**

- `EXIST` → single-use ticket → sink burns ticket → effect may run
- `NONEXIST` → signed **refusal digest** (the product, not a log line)
- `HOLD` → human review; act stays non-effective
- `otherwise` → branch witness: `agency` is `ACT` only if another **executable** write was live (`open_count >= 2`). Token samples are not histories. EXIST with one open write is `NON-ACT`.
- `nested_stit` → independent agents cannot nested-STIT. `delegated` is always false. Two different actor/principal IDs → `nst=UNSAT` on the receipt.
- `settler` → when `agency` is `NON-ACT`, who collapsed the otherwise (named `settler_id`, else allowlist/policy). The bag does not vanish.

## Wrap

```javascript
import { wrapWithRightToAct } from "@gate/right-to-act";

const guardedSend = wrapWithRightToAct(sendWire, {
  gateUrl: "https://gate.velaru.xyz",
  action: "wire.send",
  sink: "bank.rtp",
  actor: "agent-42",
  policy: { max_amount: 25, allowed_actions: ["wire.send"] },
});

const { result, right_to_act } = await guardedSend({ amount: 10, to: "acct_1" });
```

CDN:

```html
<script type="module">
  import { wrapWithRightToAct } from "https://gate.velaru.xyz/sdk/right-to-act/wrap.mjs";
</script>
```

## HTTP

- `POST /demo/right-to-act/evaluate` — public demo
- `POST /v1/right-to-act/evaluate` — evaluate CandidateAct
- `POST /v1/right-to-act/verify` — verify receipt JWT
- `POST /v1/right-to-act/burn` — sink consumes ticket (re-proves living mandate; fails on death)
- `GET /.well-known/right-to-act.json` — manifest

Related: Mandate + Mortality Clearinghouse (`/.well-known/mandate.json`) —
death certificates make burn paths non-completable for a lineage.

Prefinality is the payment-rail specialization of this substrate.
