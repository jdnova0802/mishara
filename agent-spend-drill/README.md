# Agent spend drill

A one-shot executor that tries to spend the way an autonomous agent would, against **Gate’s isolated issuing-mouth**. The public output is one word a stranger can open: **GO** or **NEVER**, plus the receipt.

This is the other half of the agent-spend-disaster story — the run where the budget does not blow. It is a fixture, not a scanner and not an orchestrator.

## What it talks to

The only tool is `POST /demo/issuing/mouth` on a **local** Gate (`http://127.0.0.1:5001` by default).

There is no in-repo staging hostname. “Staging” here means:

- loopback (or `host.docker.internal`)
- `/.well-known/issuing-mouth.json` → `money_real: false`
- the executor process has **no** `STRIPE_*` or `GATE_RECEIPT_PRIVATE_KEY`

`https://gate.velaru.xyz` is refused by name. So is every `*.velaru.xyz` host. Do not point this at production Stripe.

## Run

```bash
# terminal 1 — Gate, no Stripe keys
cd gate
./setup.sh && ./start.sh

# terminal 2
cd agent-spend-drill
python3 executor.py
# stdout: NEVER
# out/latest.html  out/latest.json
```

Open `out/latest.html`. No login. The fixture (`fixture.json`) is the agent’s goal (`$9,999.00`) and the cap it must not cross (`$50.00`). Expected word: **NEVER**.

```bash
python3 -m unittest test_drill.py
```

## Fork the fixture

Edit `fixture.json`. Keep `expected_word` honest. If you lower the goal under the cap, the mouth may answer `GO` and the drill exits 1 against this default fixture.

## What this is not

- Not a pentest of live Gate.
- Not a multi-agent graph.
- Not a clip farm.
- Not money. `write_executed` stays false; Gate does not hold funds.
