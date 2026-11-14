# Cycles live refresh

Re-pulls **only** the live splitters listed in `live_points.yaml`. It does not edit `docs/study/CYCLES_OF_CONTENTION.md` and does not know about historical crests.

```bash
cd study/cycles_live
pip install -r requirements.txt
python refresh.py --dry-run
python refresh.py
python -m unittest test_refresh.py -v
```

`--dry-run` fetches and prints the diff, then leaves the YAML alone.

A failed fetch prints `FAIL` and **does not** overwrite `last_known_value` / `last_pulled_date`. A `manual_flag` point is listed with its URL and is never scraped.

Wire this to weekly cron / GitHub Actions later if you want. There is no scheduler in this folder.

## What is automated vs flagged

Tried each source from this host (2026-11-14):

| Point | Method | Why |
|---|---|---|
| NASA GISS LOTI CSV | `api` | `GLB.Ts+dSST.csv` is a stable table |
| Eurostat `migr_asyappctza` | `api` | JSON-stat, `applicant=FRST` |
| BLS CPS weekly earnings | `api` | publicAPI v2 series LEU0252881500 / LEU0252882400 |
| CDC VSRR overdose | `api` | `data.cdc.gov` Socrata (WONDER is a form POST) |
| WaPo Fatal Force GitHub CSV | `api` | shootings, not MPV |
| EEOC Table E2c | `scrape` | listing page → official `.xlsx` (fails if the E2c link vanishes) |
| Mapping Police Violence | `manual_flag` | site 403, no public CSV |
| FBI CDE homicide rate | `manual_flag` | API key required |
| AfD / RN returns | `manual_flag` | election pages, not a live series |
| OCHA Gaza | `manual_flag` | HDX is a Google Sheet |
| Peace Now settlements | `manual_flag` | HTML only |
| Gallup climate partisan | `manual_flag` | poll HTML |
| Pew white-evangelical GOP | `manual_flag` | chart HTML |
| ECI BJP seats | `manual_flag` | PDFs; next Lok Sabha |

`YES` in the large-vs-falsifier column means the absolute (or percent) move cleared that point's `threshold`. Tune those in the YAML; do not invent a number when a fetch fails.
