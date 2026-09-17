# Join pack (bench)

Tiger tally in software. **Not Gate. Not Nisaba. Not a real harbor.**

Two halves. A time window. Draft is not go. A stranger recomputes `join_sha256`.

```bash
python3 -m join.test_pack

# seal a body, then the toy boom
python3 -m join.pack seal starter.half sealer.half body.json pack.json
python3 -m join.pack boom starter.half sealer.half pack.json
# prints GO or NO
```

`body.json` fields: `spec` (`join-pack-v1`), `what`, `not_before`, `not_after`, `starter_id`, `sealer_id`. Halves live in files, not in the pack. Same person cannot be both ids. Same half cannot seal itself.

Toy boom only prints GO/NO. It does not talk to a ship, a car, or a PLC.
