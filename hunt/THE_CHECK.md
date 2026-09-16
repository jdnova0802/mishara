# The product: the check

Picked: **better product**, not max upside. Connect week is the tail. This is the thing you can ship.

**Object:** an evidence pack the agent must emit before a human says yes.  
**Rule:** no pack, no yes. Two people recompute the same `pack_sha256`. A chat that says LGTM is the fool.

Independent of Gate. Coding-agent review fire, not a clearance mouth on a wire.

Schema (fail-closed — blanks do not print YES):

```
spec, task,
git_sha_before, git_sha_after,
commands_run[], tests_run[], tests_pass,
files_touched[], claims[],
what_it_did_not_do[],
pack_sha256
```

Code: `check/pack.py`. Verify: `python -m check.pack verify path.json`.
