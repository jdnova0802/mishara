# @gate/prefinality

Fail-closed pre-finality gate before x402 wallet sign or RTP `payment_order` create.

## x402 (before sign)

```javascript
import { wrapWithPrefinality } from "@gate/prefinality";

const secureFetch = wrapWithPrefinality(fetchWithPayment, {
  gateUrl: "https://gate.velaru.xyz",
  agentId: "researcher-01",
  mandate: { max_amount: "1.00", expected_payto: "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb" },
});

const res = await secureFetch("https://api.example.com/paid");
```

Or load from Gate directly:

```html
<script type="module">
  import { wrapWithPrefinality } from "https://gate.velaru.xyz/sdk/prefinality/wrap.mjs";
</script>
```

## RTP / FedNow (before payment_order)

1. `POST /v1/prefinality/evaluate` with `rail: "rtp"` and transfer fields.
2. On `decision: "GO"`, attach `receipt` JWT when creating PSP `payment_order` (`type: rtp`).
3. Verify with `POST /v1/prefinality/verify` or `POST /v1/prefinality/rtp/gate`.

Manifest: `/.well-known/prefinality.json`
