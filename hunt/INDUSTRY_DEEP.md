# Industry deep — circular vs posted wage (16 Sep 2026)

**Status:** hunt. Not a company. Not Flipp. Not Lightcast. Not 9am mail.  
**Parent:** `hunt/INDUSTRY_SCAN.md` (survivors only).  
**Join still:** anyone recomputes the named number from a public tape and gets the same file.

First pass said grocery circulars and legally posted wage ranges survive. Deeper: **the prices are staffed; the join is not.** And **Desk A Δ is a seller-profit object.** It maps onto grocery stickers. It does **not** map onto wages without renaming.

---

## Cut, then join

| | Grocery circular | Posted wage range |
|---|------------------|-------------------|
| Mass FOMO | Sticker, daily | Offer, when changing jobs |
| Homogeneous good | Branded UPC, yes. Produce/private label, no. | SOC + metro, messy |
| Maps to Desk A Δ | **Yes** (sellers posting prices) | **No** — that is buyer-side (oligopsony). Wrong sign if you paste Tirole’s Δ onto a wage. |
| Priest who already prints the sticker | **Flipp** (shopper). **Numerator Promo** (CPG, 800+ retailers, UPC, store). | **Lightcast** `SALARY_FROM`/`SALARY_TO`. Revelio **models** ranges onto LinkUp (not the posted sticker). |
| License-clean public tape today | Chain weekly-ad HTML (often a Flipp embed). No national archive. | **OFLC LCA** (H-1B wage vs prevailing). **USAJOBS** min/max. Not the grocery-worker offer. |
| Correlating device (do not clone) | **Revionics** / **Eversight** (Instacart) on **shelf and promo**, not the paper circular. FTC CID on Eversight (Dec 2025 reporting). | Levels.fyi / Blind (people-hunt). No-poach case law, not a SKU. |
| Fail-sale if you are not the priest | Thin: one metro AG / journalist Δ receipt. Shoppers already have Flipp. CPG already pays Numerator. | Clerk: hash of **employer-hosted** required ranges vs OEWS. HR in CO/NY/CA. Complements 6-1-1703 employment class. |
| Empty mouth | Public **join file** with frozen promo grammar, not another deals app. | Public **archive of legally required postings** you did not buy from Indeed. |

If you need one subject that is still Desk A: **grocery.**  
If you need one mouth that looks like the Colorado clerk you already built: **wage postings.**  
Do not smash them into one app.

---

## 1. Grocery circular — architecture matches Δ, rail is staffed

### What “posted” actually is

Three different numbers, often three different owners:

1. **Advertised** (weekly ad / digital circular) — loss-leader, 2-for, BOGO, “with card.”
2. **Shelf** — what Revionics/Eversight optimize. Loyalty vs regular. Instacart can differ from the store.
3. **Paid** — Circana / Numerator panel / receipt. USDA F-MAP and BLS CPI live here as aggregates.

Desk A join is (1), not (3). Calvano/Harrington are about **repeated posted prices among sellers**. Circulars are the public repeated post. Shelf RMS is the YieldStar of grocery — priest, OEM, do not clone.

### Who already sits on (1)

- **Flipp / Wishabi FlyerKit.** 2,000+ merchants. JSON products: `current_price`, `original_price`, `sku`, validity window. Token from a Flipp technical contact, not self-serve. Consumer app is free. This **is** the digital circular rail.
- **Numerator Promo Data Feeds.** 800+ retailers, 265 markets, UPC + store, 70+ promo attributes, prior-week lag. Sold to CPG trade-spend teams. CGPI (Aug 2026 print: +2.2% YoY) is **paid** prices from ~200k households, not ads.
- Shopper layer: Flipp, Basket (crowdsourced **shelf**), Instacart, Ibotta. Australia is further along on basket comparison (TrolleyChecker / WiseList). You are not in an empty consumer market.

Apify “Flipp scrapers” are not a rail. ToS war. Kill.

### Why first pass overstated “nobody owns advertised Δ”

They own the **stickers**. They do not publish a **join**: frozen grammar → π̄, πN, πM → one Δ per UPC–week–market that a stranger recomputes from hashed sources.

Numerator sells “did my brand win promo share.” Flipp sells “milk is cheap at this store.” Neither sells Tirole’s Δ.

### Frozen grammar (or Δ is a vibe)

Without these rules, two people never match:

| Promo text | Rule |
|------------|------|
| `$2.49` | π = 2.49 |
| `2 for $5` | π = 2.50 per unit, flag `multi` |
| `BOGO` | π = 0.5 × reference, flag `bogo` (reference = `original_price` if present, else drop row) |
| `with card` / loyalty | keep, flag `loyalty`. Do not mix with regular in the same Δ. |
| `$1.99 lb` vs `12 oz` | convert to **price per ounce or per pound**; drop if unit missing |
| No UPC | **drop from Δ**. Name-only match is a priest. Private label is a unique good. |
| Produce | kill for v1. Not a UPC. |
| Missing rival that week | **no Δ**. Do not impute. Fail-closed. |

**π̄** = this chain’s advertised unit price (after grammar).  
**πN** = min advertised unit price among **other** chains in the same ZIP-3 (or listed store set) that week, same UPC, same loyalty flag.  
**πM** = max advertised among that set.  

That is **not** Tirole’s profit Δ. It is a **posted-price spread index** on the same SKU. Call it **S**, not Δ, until you have margins. Using monopoly-profit Δ on grocery ads without cost is a lie. Honest join:

**S = (p̄ − p_min) / (p_max − p_min)** when p_max > p_min, else 0.  
Anyone with the tape file gets the same S.

If you later have costs, *then* Desk A Δ. Do not pretend S is Δ.

### Tape row (the object)

```
week_start, zip3, chain, store_id, upc, unit, advertised_unit_price,
loyalty, grammar, source_url, fetched_at, sha256
```

`sha256` hashes the fetched bytes (HTML/JSON you were allowed to fetch), not your opinion.

### Fail-sale, empty vs staffing

- **Do not** sell a Flipp. **Do not** sell Numerator to CPG.
- Remaining mouth: a **fail-closed S receipt** for one metro, 3 chains, ~20 national UPCs, 12 weeks — journalists / a state AG / a seminar, maybe a $5–8k diligence-shaped review of “are these ads a focal schedule.” That is not Twitter wealth.
- Shelf RMS (Revionics Gartner 2026 UPPMO; Eversight under FTC attention) is the dual-use later hope and **not yours to productize**.

### If you ever code (not tonight)

One ZIP-3 you can walk. Three chains that host a weekly ad URL without a login. Twenty branded UPCs (eggs gallon milk not required if they lack UPC; use Cheerios 18oz etc.). Grammar table above. No Flipp token. Rows that fail grammar do not print S.

---

## 2. Posted wage — clerk maps, Δ does not

### Sign error (do not skip)

Desk A: high **price/profit** → collusion among **sellers**.  
Labor: low **wage** → collusion among **buyers** (oligopsony / no-poach / wage-fixing).

If you compute (w̄ − w_Nash) / (w_monopsony − w_Nash) with w_monopsony < w_Nash, you need a **labor** index, not Tirole’s Δ copied onto dollars-per-hour.

Name it **Λ** (or leave it unnamed until Cover/Tirole/Osborne are done). Example freeze, competitive high, monopsony low:

**Λ = (w_comp − w̄) / (w_comp − w_mono)**  
clipped to [0,1] when the denominator is positive.

**w̄** = posted **minimum** (good-faith floor; freeze this, not midpoint — midpoint rewards wide fake ranges).  
**w_comp** = OEWS **75th** (or 90th — freeze one) for SOC + MSA, same pay unit.  
**w_mono** = OEWS **10th** for that cell.

Anyone with posting HTML + OEWS xlsx + this paragraph gets the same Λ. Midpoint vs min is how you stay a 6.

Wide posted ranges ($50k–$180k) are **not** Λ. They are a **compliance defect** (Colorado INFO #9A: cannot post janitor and accountant on the same cartoon span). Separate clerk: **range_width / OEWS_IQR**. Fail-sale sits here more than in Λ.

### Who already sits on wages

| Source | What it is | Join? |
|--------|------------|-------|
| Lightcast US postings | Advertised `SALARY_FROM`/`TO`, SOC, daily, priest, $ | Their tape, not yours |
| Revelio × LinkUp | **Modeled** salary on every listing back to 2007 | Not posted. Kill for join. |
| OFLC LCA FY2026 Q3 (released 14 Aug 2026) | Employer, `WAGE_RATE_OF_PAY_FROM`, `PREVAILING_WAGE`, SOC, worksite. Public xlsx. | **Yes**, H-1B only. Every immigration shop already charts this. |
| USAJOBS HistoricJoa | `minimumSalary` / `maximumSalary`, series, GS. Public API. | **Yes**, federal only. GS **is** the correlating device. |
| OEWS May 2025 | Occupation × area percentiles. Public. | πN-class **index**, not the offer. |
| Levels.fyi / Blind / Glassdoor | People-hunt + priest | Kill |
| CDLE | Enforces EPEWA. **Does not publish a tape of all CO postings.** | No archive |

Pay-transparency posting (Jackson Lewis 2026 roundup, live): CO (1+ employee, range + benefits + deadline), CA (15+, SB 642 1 Jan 2026), NY (4+), WA (15+), MA (25+, posting duty since 29 Oct 2025). Geography is real. A national Indeed scrape is still a priest.

### Tape row (the object)

```
posted_at, employer, title, soc, msa, wage_min, wage_max, unit,
benefits_flag, apply_deadline, source_url, fetched_at, sha256
```

SOC is assigned by a **published crosswalk you freeze** (title string → SOC). If the crosswalk cannot assign, **drop**. Do not LLM-assign in the join path.

### Fail-sale, empty vs staffing

Lightcast already sold the board scrape to HR and economists.  
Empty: **employer-hosted** required postings (careers.example.com), hashed, compared to OEWS — a **packet**, not a Glassdoor.

Buyer: Colorado (and NY/CA) employers who must post a good-faith range and will pay a clerk to show the range is not a cartoon vs OEWS. Same motion as `assessment/` — paper that says they used care. Not Mishara. Not a negotiation bot.

H-1B LCA: public join already exists; do not found MyVisaJobs.

USAJOBS: public join already exists; do not found a GS decoder.

### If you ever code (not tonight)

Pick **Colorado employer career pages you are allowed to fetch** (their own `robots.txt`). Ten employers, one MSA (Denver-Aurora-Lakewood), titles that map cleanly to OEWS (registered nurse, accountant, not “rockstar ninja”). Freeze min, not mid. Print range_width / OEWS_IQR. Λ only after the wage dual is written down next to Tirole, not instead of it.

---

## 3. What this does to the stack

Study 3 is still **oligopoly Δ on seller profits**.  
Grocery **S** is a posted-price cousin you may compute on a tape.  
Wage **Λ** is a **different subject** (oligopsony). Do not sneak it into join as if it were Δ. That would make the years object a 6 again.

Cover → Osborne → Tirole Δ stays the night work. This memo is the industry cut, not a seventh class.

---

## 4. Pick (not found)

**Closer to Desk A (architecture):** grocery **S** on a 20-UPC, 3-chain, 1-metro circular tape. You will look small next to Flipp/Numerator. That is correct.

**Closer to a quit-the-cleaning-job clerk:** CO **range packet** vs OEWS, employer-hosted URLs, fail-closed blanks. Same family as 6-1-1703 assessment. Still not Mishara.

**Do not:** Flipp clone, Lightcast clone, Instacart price experiments, Revionics, people-hunt salaries, mixing S and Λ in one dashboard, pivoting T1–T3.

Tape formats above are the quark. If you pick one, the next object is a **schema + fixture rows**, not a Twitter account.
