# Class & Social Mobility Map

Descriptive / institutional reference. **What is being measured, by whom, on which data — and which adjacent measure it is not.** Not a history of inequality and not a policy brief. Primary sources first. Wikipedia is a finding aid. OPEN rather than invented. Pull date **2026-11-14**. Companion to the Atlas and the Religion / Standards / War maps — **not** the same field grid. Standing rules: [`docs/study/STUDY_SERIES_RULES.md`](STUDY_SERIES_RULES.md).

Do not mash machines. An **IGE** (intergenerational income elasticity) is not a rank-rank slope. Chetty’s 2014 “absolute **upward** mobility” (expected child rank at parental 25th percentile) is not Chetty’s 2017 “absolute **income** mobility” (share of children who out-earn their parents). Income mobility is not wealth mobility. A randomized housing experiment is not an observational atlas. Bourdieu’s capitals are not a regression coefficient.

---

## How to read an entry

Every entry uses the same fixed **11-field** template. Field labels stay in this form throughout. In any **Falsifier** line, “cell N” means field N on this list (so “cell 5” is Named finding).

1. **Mechanism/concept name**
2. **Type** — quantitative mobility measure / capital-type framework / structural channel / comparative framework
3. **Operational definition** — the formula or definition researchers actually use
4. **Data source** — named dataset and the institution/team that built it
5. **Named finding** — the figure, tied to a named study and year
6. **What this is NOT** — the adjacent, frequently-confused measure (the counting-machines cell)
7. **Scope/population** — who is covered; who is excluded; cohort/years
8. **Named case or comparison**
9. **Falsifier** — the fact that would disprove cell 5
10. **OPEN** — disputed methodology, data gaps; not estimated
11. **Primary sources**

---

### Intergenerational income elasticity (IGE)

1. **Name:** Intergenerational income elasticity (**IGE**). Common: “how much of your parents you inherit,” mashed with a rank correlation.
2. **Type:** Quantitative mobility measure.
3. **Operational definition:** **OLS** (ordinary least squares) coefficient β in  
   `ln Y_child = α + β ln Y_parent + ε`  
   where Y is a measure of “permanent” earnings or family income. β is the **percent** difference in child’s income associated with a 1 percent difference in parent’s income. Higher β = more persistence = **less** mobility. Corak (**JEP** (Journal of Economic Perspectives) 2013) writes the same equation as `ln Y_{i,t} = α + β ln Y_{i,t−1} + ε_i`.
4. **Data source (do not mash):**
   - **Solon 1992:** **PSID** (Panel Study of Income Dynamics), University of Michigan Survey Research Center, nationally representative longitudinal survey since 1968. Father–son sample on the order of **348** pairs in the main earnings analysis.
   - **Mazumder 2005:** **SIPP** (Survey of Income and Program Participation, 1984) matched to **SSA** (Social Security Administration) **SER** (Summary Earnings Records).
   - **Chetty, Hendren, Kline, Saez 2014:** de-identified **US** (United States) federal income-tax records (more than 40 million children); **IRS** (Internal Revenue Service) / **SOI** (Statistics of Income) under IRS contract TIRNO-12-P-00374. Later hosted by Opportunity Insights (Harvard).
5. **Named finding:**
   - Solon, “Intergenerational Income Mobility in the United States,” **AER** (*American Economic Review*) 82(3) 1992: long-run father–son correlation/elasticity “**at least 0.4**”; multi-year averages of father’s log earnings sit “in the neighborhood of 0.4.”
   - Mazumder, “Fortunate Sons,” **REStat** (*Review of Economics and Statistics*) 87(2) 2005: with long SSA earnings histories the IGE is “**around 0.6**”; 5-year averages are biased down ~30% by persistent transitory shocks.
   - Chetty et al., “Where is the Land of Opportunity?,” **QJE** (*Quarterly Journal of Economics*) 129(4) 2014: baseline log-log IGE **0.344** (excluding zeros); restricting parents to the 10th–90th percentiles and dropping zero-income children yields **0.45**; “alternative specifications yield IGEs ranging from **0.26 to 0.70**.”
6. **What this is NOT:** Not a **rank-rank slope** (next entry). Not a Gini coefficient. Not the share of children who out-earn their parents. Not a wealth elasticity. **Do not** report Mazumder’s 0.6 as if it were Chetty’s 0.341 rank-rank, or Solon’s 0.4 as if it were a transition probability.
7. **Scope:** Solon: PSID fathers/sons, earnings/wages/family income, late 1960s–early 1980s measurement years. Mazumder: SIPP-SSA, fathers and sons (daughters nearly identical in that paper); SSA top-coding **OPEN** as a limitation he flags. Chetty et al. 2014: children born **1980–1982**, parent income when children are ~15–20, child income ~age 30; tax universe, zeros dropped in the log-log IGE.
8. **Named case:** United States father–son earnings IGE versus Corak’s Nordic estimates (Denmark/Norway/Finland “less than one-fifth”) — those Nordic numbers are **other studies Corak homogenized**, not Solon’s PSID (see Great Gatsby Curve entry).
9. **Falsifier:** If Solon 1992 Table 3 multi-year estimates were ~0.2 rather than ~0.4, cell 5’s “at least 0.4” dies. If Mazumder’s 16-year SSA average produced 0.4, not ~0.6, that named finding dies. If Chetty’s log-log IGE were invariant to zeros and to the 10–90 restriction, the 0.26–0.70 range in that paper dies.
10. **OPEN:** Which US IGE is “the” number — Solon ~0.4, Mazumder ~0.6, Chetty 0.34/0.45/0.26–0.70 — is a **specification and dataset** dispute, not a fact to average. Lifecycle bias (Haider–Solon 2006) and SSA censoring remain live. **NLSY** (National Longitudinal Surveys of Youth, US Bureau of Labor Statistics) estimates are a **third** survey machine — not copied this pass.
11. **Sources:** Solon, *AER* 1992, 82(3): 393–408; Mazumder, *REStat* 2005, 87(2): 235–255; Chetty, Hendren, Kline, Saez, *QJE* 2014, 129(4): 1553–1623, https://opportunityinsights.org/paper/land-of-opportunity/ ; Corak, *JEP* 2013, 27(3): 79–102 (formula).

---

### Rank-rank slope and Chetty “absolute upward mobility”

1. **Name:** Rank-rank slope, plus Chetty et al. 2014’s **absolute upward mobility** = expected child income **rank** given parents at the **25th** percentile. Common: “Chetty’s mobility number,” mashed with IGE and with 2017 absolute *income* mobility.
2. **Type:** Quantitative mobility measure.
3. **Operational definition:** Rank children by income within birth cohort (zeros **included**); rank parents among parents of those cohorts. Slope = OLS coefficient in  
   `child_rank = α + ρ parent_rank + ε`  
   with ranks in percentiles 0–100. Chetty et al. 2014: “absolute upward mobility” at p = 25 is the fitted **mean child rank** when parent rank = 25 (linearity of the rank-rank line makes this the mean rank for the bottom half). Separately they report P(child in national top quintile | parent in bottom quintile).
4. **Data source:** Same tax-record core as Chetty et al. *QJE* 2014: more than 40 million children, 1980–82 birth cohorts; Opportunity Insights / IRS. Rank-rank as a design: Dahl and DeLeire 2008 (cited by Chetty as the similar specification).
5. **Named finding:** Chetty, Hendren, Kline, Saez *QJE* 2014:
   - Rank-rank slope **0.341**: “a 10 percentile increase in parent income is associated with a 3.4 percentile increase in a child’s income.”
   - National P(top quintile | bottom quintile) = **7.5%** (core sample, Table II).
   - Geography: that probability is **4.4%** in Charlotte, **12.9%** in San Jose; among the 50 largest **CZs** (commuting zones) absolute upward mobility at p=25 ranges **35.8** (Charlotte) to **46.2** (Salt Lake City).
6. **What this is NOT:** **Not an IGE.** Chetty’s own log-log IGE is a different cell (0.344 / 0.45). **Not** “The Fading American Dream” (2017) absolute *income* mobility (percent who out-earn parents). The phrase “absolute mobility” is used for **both** machines in the Chetty corpus — **do not collapse the names**. Rank-rank is relative stickiness in ranks; p=25 expected rank is a **level** on a relative scale, still not dollars-versus-parents.
7. **Scope:** US children born 1980–82 linked to parents on tax forms; child family income ~age 30; assigned to CZ of childhood (~age 16). National ranks, not within-CZ ranks, for the geographic comparisons.
8. **Named case:** Charlotte vs San Jose bottom-to-top quintile (4.4% vs 12.9%); Denmark comparison in the same paper: US 7.5% vs Denmark **11.7%** (Boserup, Kopczuk, Kreiner cited) — a **transition probability**, not Denmark’s IGE.
9. **Falsifier:** If the *QJE* 2014 rank-rank slope were not ~0.34 (or if zeros were excluded and the slope jumped into the IGE 0.26–0.70 band as if they were the same statistic), cell 5 dies. If Charlotte’s bottom-to-top probability were 12.9%, the geographic contrast dies.
10. **OPEN:** Later Opportunity Insights papers use overlapping but not identical cohorts and income definitions — **do not splice 2014 ρ with 2020 race-paper intercepts as one number**. Cost-of-living adjustments are reported as robustness, not as a second national slope.
11. **Sources:** Chetty et al., *QJE* 2014, 129(4): 1553–1623 and Online Data Tables I–II, VII; https://opportunityinsights.org/paper/land-of-opportunity/

---

### Absolute income mobility (“The Fading American Dream”)

1. **Name:** Absolute **income** mobility — fraction of children who earn more than their parents at the same age, inflation-adjusted. Chetty, Grusky, Hell, Hendren, Manduca, Narang, “The Fading American Dream,” *Science* 356(6336) 2017.
2. **Type:** Quantitative mobility measure.
3. **Operational definition:** Compare child’s household income at **age 30** to parents’ household income at age 30, in real dollars (**CPI** (Consumer Price Index) in the baseline). Absolute mobility rate = share of children with income_child > income_parent. Early cohorts lack parent–child panels: authors combine Census/**CPS** (Current Population Survey) **marginal** distributions with a rank copula taken from 1980s tax data (copula-stability assumption).
4. **Data source:** Census and CPS cross-sections 1940–2014 for marginals; de-identified tax records for the 1980–82 copula (Chetty et al. 2014 Online Data Table 1); Opportunity Insights replication package.
5. **Named finding:** *Science* 2017 and the full working paper:
   - **92%** of children born in **1940** earned more than their parents; **50%** of children born in **1984**.
   - Abstract rounding: “approximately **90%** … to **50%** for children born in the 1980s.”
   - Sons vs fathers’ individual earnings: **95%** (1940) to **41%** (1984).
   - At the parental median: **93%** (1940) to **45%** (1980).
   - Counterfactuals: restore 1940s **GDP** (Gross Domestic Product) growth with today’s distribution of growth → mobility only to **62%**; keep today’s GDP level but 1940s distribution of growth → **80%**.
6. **What this is NOT:** Not the 2014 rank-rank slope. Not 2014 “absolute upward mobility” (mean **rank** at p=25). Not IGE. A 50% out-earn rate can coexist with a stable rank-rank slope: ranks can stick while the dollar ladder stops rising. **Do not** say “mobility halved” as if ρ went from 0.34 to 0.17.
7. **Scope:** US-born, non-institutionalized at age 30; immigrants excluded from the child sample for consistency. Birth cohorts **1940–1984**. Baseline: pre-tax family income, CPI deflator, age 30.
8. **Named case:** All 50 states show declines 1940→1980; largest in industrial Midwest (Michigan, Illinois named). Sons–fathers series is a **different income concept** than the household baseline — report both, do not average 50% with 41%.
9. **Falsifier:** If the 1940 cohort’s baseline rate were ~50% rather than ~92% under the paper’s own copula-stability benchmark, cell 5 dies. If switching deflator (they test alternatives) reversed the decline, the robustness claim in the paper would die — they report it does **not**.
10. **OPEN:** Copula stability 1940–80 is an **assumption** (they bound 1940 between 84% and 98% across all copulas). Later-life (age 40) and after-tax variants are in the appendix; do not substitute them for 92/50 without naming the variant.
11. **Sources:** Chetty, Grusky, Hell, Hendren, Manduca, Narang, *Science* 2017, 356(6336): 398–406; paper PDF https://opportunityinsights.org/paper/the-fading-american-dream/ ; replication tables.

---

### The Great Gatsby Curve (Corak)

1. **Name:** **Great Gatsby Curve** — cross-national plot of inequality against intergenerational earnings persistence. Named by Alan Krueger; empirical compilation by **Miles Corak**, *JEP* 27(3) 2013.
2. **Type:** Comparative framework (not a within-country statistic).
3. **Operational definition:** Horizontal axis: **Gini** coefficient of disposable household income, **OECD** (Organisation for Economic Co-operation and Development), ~early/mid-1980s. Vertical axis: father–son **earnings IGE** for children born ~early/mid-1960s, adult outcomes ~mid/late 1990s, from published studies **adjusted for comparability** (Corak 2006 appendix method, updated 2013). The curve is a **cross-country scatter**, not a causal slope estimated from a single micro dataset.
4. **Data source:** OECD Ginis; IGE estimates compiled by Corak from national studies (PSID, Nordic registers, etc.). **Do not** treat the homogenized IGE axis as Solon 1992 raw.
5. **Named finding:** Corak *JEP* 2013: countries with more inequality also have less earnings mobility across generations. Nordic IGE “less than one-fifth”; “Italy, the United Kingdom, and the United States roughly **50 percent**” of advantage passed on. That US ~0.5 is **Corak’s comparability-adjusted compilation**, not Chetty’s 0.341 rank-rank and not automatically Mazumder’s 0.6.
6. **What this is NOT:** Not a US time series. Not Chetty geography. Not a proof that inequality **causes** immobility (Corak presents drivers — families, labor markets, policy — not an identified β). Not the 2017 absolute-income-mobility decline.
7. **Scope:** High-income countries in Corak’s Figure 1; father–son earnings, not household income, not wealth, not daughters (he flags that limitation).
8. **Named case:** United States / United Kingdom vs Denmark / Norway / Finland / Sweden on that figure. US–Canada decile transition comparison in the same article (Corak 2010 cited) is a **second** machine.
9. **Falsifier:** If Corak’s Figure 1 placed the US IGE with the Nordics after his own adjustments, cell 5 dies. If the Gini axis were contemporaneous 2010s Ginis rather than ~1985 OECD, it would be a different figure — he specifies the lag.
10. **OPEN:** Cross-country IGE comparability (age, years averaged, earnings vs income). Whether the US IGE **rose** with the college premium (Aaronson–Mazumder 2008 / Mazumder 2012 vs Mayer–Lopoo 2004 and Lee–Solon 2009 finding **no** significant US IGE trend) — Corak footnotes the disagreement; **do not pick a winner here**.
11. **Sources:** Corak, *JEP* 2013, 27(3): 79–102, https://www.aeaweb.org/articles?id=10.1257/jep.27.3.79 ; PDF https://milescorak.com/wp-content/uploads/2013/07/income-inequality-equality-of-opportunity-and-intergenerational-mobility.pdf

---

### Education as a mobility channel (Mobility Report Cards)

1. **Name:** College **mobility report cards** — access, success, and mobility rates by parental income and college. Chetty, Friedman, Saez, Turner, Yagan, **NBER** (National Bureau of Economic Research) Working Paper 23618 (2017) and *QJE* 135(3) 2020.
2. **Type:** Structural channel (higher education), measured with quantitative access/mobility rates.
3. **Operational definition:** For each college: **access** = share of students from the bottom parental-income quintile; **success** = share of those bottom-quintile students who reach the top quintile of the child earnings distribution; **mobility rate** = access × success = share of *all* students at the college who are bottom-quintile origin **and** top-quintile outcome. “Ivy-Plus” = eight Ivy League colleges plus Duke, **MIT** (Massachusetts Institute of Technology), Stanford, and the University of Chicago.
4. **Data source:** Federal income-tax records linked to Department of Education college attendance; **>30 million** college students, 1999–2013 (NBER Working Paper 23618). Baseline children born **1980–82**; college attended most at ages 19–22; child earnings ages **32–34**. 2020 *QJE* paper adds **SAT** (College Board admissions test) / **ACT** (college admissions test) scores to study allocation vs undermatch.
5. **Named finding:**
   - Ivy-Plus: **3.8%** of students from the bottom quintile; **14.5%** from the top **1%** (family income > **$532,000** in 2015 dollars) vs **13.5%** from the **bottom half**. Children from the top 1% are **77 times** more likely to attend Ivy-Plus than children from the bottom quintile.
   - National average college bottom-to-top mobility rate **1.7%** (perfect-mobility benchmark **4%**).
   - **Stony Brook** (State University of New York at Stony Brook): **16.4%** bottom-quintile access, mobility rate **8.4%** vs Ivy-Plus mobility rate **2.2%** (high success, thin access).
   - **CUNY** (City University of New York), some California State campuses, some University of Texas campuses: mobility rates **above 6%**.
   - Conditional on test scores (*QJE* 2020): equalizing attendance given scores would cut low-income under-representation at selective schools by **38%**; Ivy-Plus bottom-quintile share would rise only **3.8% → 4.4%**.
6. **What this is NOT:** Not the causal effect of attending a given college (the 2017 paper: “descriptive analysis does not identify colleges’ causal effects”). Not K–12 test-score gaps. Not IGE. Mobility **rate** is not success **rate** — Ivy-Plus looks strong on success and weak on access.
7. **Scope:** Students linked to tax parents; non-college youth are outside college-level cards. Tiers from Department of Education / College Scorecard characteristics. Closed colleges as of 2019 have a separate crosswalk.
8. **Named case:** Ivy-Plus vs Stony Brook vs CUNY as above. Upper-tail (bottom quintile → top **1%**) success ~**13%** at elite privates — a **different success definition**; no high-access college matches that upper-tail success.
9. **Falsifier:** If Ivy-Plus bottom-quintile share were ~16% rather than 3.8% in WP 23618 / *QJE* 2020, cell 5 dies. If mobility rate were defined as success alone, Stony Brook would not outrank Ivy-Plus on that statistic.
10. **OPEN:** Causal value-added of colleges vs selection. How 2000–2011 declines in access at high-mobility public campuses affect later cohorts. Test-score “Ivy-Plus 160 SAT-point” equivalences in the 2020 paper are **counterfactuals**, not admissions-office rules.
11. **Sources:** Chetty, Friedman, Saez, Turner, Yagan, NBER WP 23618 (2017); *QJE* 2020, 135(3): 1567–1633; https://opportunityinsights.org/paper/mobilityreportcards/

---

### Neighborhood: Moving to Opportunity (randomized)

1. **Name:** **MTO** (Moving to Opportunity) long-run child earnings — Chetty, Hendren, Katz, *AER* 106(4) 2016.
2. **Type:** Structural channel, identified by **randomized experiment**.
3. **Operational definition:** **HUD** (US Department of Housing and Urban Development) 1994–98 experiment. Eligible families in high-poverty public housing randomized to (i) experimental voucher usable (year 1) only in census tracts with 1990 poverty **<10%**, (ii) standard Section 8 voucher, (iii) control (stay eligible for public housing). **ITT** (intent-to-treat) = OLS on assignment. **TOT** (treatment-on-the-treated) = **IV** (instrumental variables): assignment instruments for voucher take-up. Young children: age **<13** at random assignment.
4. **Data source:** MTO participant files (4,604 households; 15,892 individuals) under HUD Data License DL14MA001, linked by Social Security number to federal tax returns 1996–2012. Five cities: Baltimore, Boston, Chicago, Los Angeles, New York.
5. **Named finding:** Chetty, Hendren, Katz *AER* 2016: children whose families **take up** the experimental voucher before age 13 have annual income **$3,477 (31%)** higher on average relative to control mean **$11,270** in their mid-twenties (TOT). ITT on college attendance ages 18–20: **+2.5 percentage points (16%)** vs control **16.5%**. Same moves: **if anything negative** for children older at move. Experimental TOT on income about **twice** Section 8 TOT ($1,723), in line with larger poverty-rate reductions.
6. **What this is NOT:** Not the Opportunity Atlas (next entry) — Atlas is population observational / mover quasi-experiment, not MTO randomization. Not adult MTO health findings (Kling, Liebman, Katz 2007; Sanbonmatsu et al. 2011) as if they were child earnings. Not a national mobility slope.
7. **Scope:** Families who **volunteered** from public housing in five cities; extremely disadvantaged (not a random poor sample). Tax link: 86.4% of younger children, 83.8% of older. Outcomes through 2012 (early thirties at most).
8. **Named case:** Five-city MTO; young vs old split at 13. Lifetime earnings projection in the paper (~$302,000 undiscounted TOT for young experimental movers) is a **projection**, not a realized panel to retirement — flag as such.
9. **Falsifier:** If TOT earnings for young experimental movers were zero (or negative) in the tax-linked *AER* 2016 tables, cell 5 dies. If young and old treatment effects were equal, the age-at-move claim dies.
10. **OPEN:** External validity beyond MTO volunteers and five cities. Small N at each single year of age (they say so). Earlier MTO short-run tests on adults are a **different outcome machine**.
11. **Sources:** Chetty, Hendren, Katz, *AER* 2016, 106(4): 855–902; PDF https://opportunityinsights.org/wp-content/uploads/2018/03/mto_paper.pdf

---

### Neighborhood: Opportunity Atlas (observational / causal-inference)

1. **Name:** Opportunity Atlas — Chetty, Friedman, Hendren, Jones, Porter, Census-tract outcomes by parental income, race, and gender. *AER* 116(1) 2026 (working paper 2018).
2. **Type:** Structural channel, **observational** tract estimates plus **quasi-experimental** mover design — not MTO.
3. **Operational definition:** For each 2010 Census tract (and county/CZ), estimate children’s adult household income, incarceration, etc., by parental income percentile, race, and gender. Causal claim in the paper: observational tract estimates **predict** causal neighborhood effects when compared to MTO and to a movers design (Chetty–Hendren exposure). Granularity: characteristics of tracts **one mile away** have little predictive power once own-tract poverty is controlled.
4. **Data source:** Anonymized longitudinal data covering nearly the entire US population; Census Bureau Disclosure Review Board. Public tract tables at Opportunity Insights. Childhood cohorts in public low-income files include **1984–1989** (see data documentation on the paper page).
5. **Named finding:** For children of parents at the **25th** percentile, the standard deviation of mean household income at **age 35** is **$5,000** across tracts **within counties**. Historical tract estimates remain predictive because neighborhood conditions are relatively stable. Weak correlation with job-growth proxies for “local economic success.”
6. **What this is NOT:** Not MTO (no random assignment of Atlas families). Not CZ-level Chetty 2014 tables (tract is finer; income year/age differ). Not a Gini. Do not quote $5,000 as a treatment effect of moving.
7. **Scope:** Nearly all US children in the linked Census/tax universe who can be assigned a childhood tract. Public tables suppress/disclosure-limit small cells.
8. **Named case:** Within-county tract dispersion ($5,000 standard deviation at p=25). Affordable high-opportunity tracts as a targeting input (paper’s housing-policy application) — that application is **not** a second experiment.
9. **Falsifier:** If within-county tract standard deviation of p=25 child household income at 35 were negligible in the Atlas tables, cell 5 dies. If Atlas observational ranks failed to predict MTO/mover causal effects as the paper claims, the “highly predictive of causal effects” sentence dies.
10. **OPEN:** How much of tract variation is causal vs selection after the mover adjustment. 2020 tract vintage vs 2010 crosswalk. Race-by-tract cells in the Atlas vs the 2020 race *QJE* (next entry) use overlapping but not identical samples — **do not mash percentiles across papers**.
11. **Sources:** Chetty, Friedman, Hendren, Jones, Porter, *AER* 116(1) 2026: 1–51; https://opportunityinsights.org/paper/the-opportunity-atlas/

---

### Racial mobility gap (Chetty, Hendren, Jones, Porter)

1. **Name:** Black–white intergenerational income gap **conditional on parent income**, gender-split. Chetty, Hendren, Jones, Porter, *QJE* 135(2) 2020.
2. **Type:** Quantitative mobility measure (by race and gender).
3. **Operational definition:** Race-specific rank-rank lines: `E[child rank | parent rank, race] ≈ α_r + β_r parent_rank`. Gap at a given parent percentile = difference in mean child ranks. Household vs individual income are **separate** Y variables. Incarceration, employment, wages reported as mechanisms, not as substitutes for the income rank.
4. **Data source:** De-identified longitudinal data covering nearly the entire US population **1989–2015**; Census Bureau Disclosure Review Board (**CBDRB**) release FY18-195. Opportunity Insights Online Data Tables 1–7.
5. **Named finding:** *QJE* 2020:
   - White children with parents at p=25 reach the **45th** percentile on average; Hispanic **43rd**; Asian **56th**; Black children ~**13 percentiles** lower than whites across the parent distribution (household income).
   - **The household-income Black–white gap is driven by men:** ~**10 percentile** individual-income gap for Black vs white **men** conditional on parent income; Black **women** earn about **1 percentile more** than white women conditional on parent income.
   - Individual-income Black–white gap ~**5 percentiles** vs ~**13** for household income (marriage/spouse earnings).
   - Parental marital status: men’s gap **10 → 9.3** percentiles — “very little.” Tract/block fixed effects: among p=25 parents, Black–white boy individual-income gap **7.7** (tract) / **7.0** (block). Black boys have lower adult incomes than white boys in **99%** of Census tracts.
   - Incarceration: **21%** of Black men vs **6%** of white men in their data (as reported in the paper’s gender-gap discussion).
6. **What this is NOT:** Not a raw median Black–white wage gap unconditioned on parents. Not IGE by race (they use ranks). Not “no gap for women” in **household** income. Not the Atlas $5,000 SD. Hispanic and Asian series are **other** race lines — do not average them into the Black–white gap.
7. **Scope:** Children whose race is observed in Census/tax links; immigrant-origin tables are separate (Online Tables 6a/6b). Outcomes in the mid-30s. Neighborhood results: boys, parental income controls.
8. **Named case:** Silver Spring, Maryland, and parts of Queens, New York — named as rare low-poverty, low-white-bias, high-Black-father-presence areas where low-income Black boys exceed the national median; “fewer than 5% of Black children grow up in such environments.”
9. **Falsifier:** If, conditional on parent income, Black and white **men’s** individual ranks were equal in Table 1 of this paper, cell 5 dies. If the gap were “driven by daughters,” the gender split dies.
10. **OPEN:** Translation from ranks to dollars (they point to Chetty et al. 2017 methods). Causal share of neighborhood vs discrimination vs other — they show persistence **within** tracts, not a full decomposition. American Indian mobility is documented as similarly low; not merged into the Black–white cell.
11. **Sources:** Chetty, Hendren, Jones, Porter, *QJE* 2020, 135(2): 711–783; https://opportunityinsights.org/paper/race/

---

### Wealth mobility vs income mobility

1. **Name:** Intergenerational **wealth** elasticity, contrasted with income IGE. Why wealth is **sparser**.
2. **Type:** Quantitative mobility measure (wealth) plus a data-structure fact.
3. **Operational definition:** Charles and Hurst: OLS of log child’s wealth on log parent’s wealth, age-adjusted, **before bequests**. Coefficient = wealth IGE. **SCF** (Survey of Consumer Finances), Board of Governors of the Federal Reserve System: triennial **cross-section** of US family balance sheets — **not** a parent–child panel. SCF dual frame: area-probability sample plus **list oversample** of likely-wealthy families from SOI tax files (Kennickell), because wealth is in the tail.
4. **Data source:**
   - Charles and Hurst, *JPE* (*Journal of Political Economy*) 111(6) 2003: **PSID** parent–child pairs (both generations alive; 1984/1989/1999 wealth modules).
   - SCF: Federal Reserve triennial interview survey, modern series since **1989** (2022 wave: **4,602** families interviewed; five implicates). https://www.federalreserve.gov/econres/scf_2022.htm
5. **Named finding:**
   - Charles and Hurst *JPE* 2003: age-adjusted intergenerational **wealth** elasticity **0.37** before bequests; lifetime income and asset ownership jointly explain nearly **two-thirds** of that elasticity.
   - SCF 2022 Bulletin (Federal Reserve, 2023): real **median** net worth **+37%** and mean **+23%** from 2019–22 — a **repeated cross-section** of the wealth *stock*, **not** an intergenerational elasticity. Cite it only as the wealth-measurement machine, not as mobility.
6. **What this is NOT:** **0.37 is not Solon’s 0.4 income IGE and not Chetty’s 0.341 rank-rank.** SCF medians are not parent–child transitions. Income tax records (Chetty) measure **income** well and **taxable capital income** incompletely; they are not a wealth panel. **Do not** impute a wealth rank-rank from Opportunity Insights income ranks.
7. **Scope:** Charles–Hurst: PSID pairs with observed wealth, survivors, pre-bequest. SCF: US families; public file drops a handful of records for disclosure; Asian wealth in older waves **under-powered** until the 2022 minority oversample (Fed note 2021 / 2022 redesign).
8. **Named case:** Why wealth data are sparser than income data: (i) SCF is triennial cross-section, ~4.6–5.8k families, not 40 million tax children; (ii) wealth is extremely skewed, so the survey **must** oversample the right tail; (iii) PSID wealth is a smaller longitudinal module; (iv) bequests arrive late, so most of adult life is pre-bequest (Charles–Hurst’s own scope limit).
9. **Falsifier:** If Charles–Hurst’s age-adjusted elasticity were 0.04, not 0.37, cell 5 dies. If the SCF were a linked parent–child administrative wealth register covering the US population, the “sparser” claim in cell 8 would need a rewrite.
10. **OPEN:** Post-bequest wealth persistence (they cannot measure it in that sample). Pfeffer–Killewald multigenerational PSID wealth correlations are a **later** machine — not copied this pass. Capital-gains basis and private-business valuation in both PSID and SCF.
11. **Sources:** Charles and Hurst, *JPE* 2003, 111(6): 1155–1182; Federal Reserve SCF 2022, https://www.federalreserve.gov/econres/scf_2022.htm ; Bhutta et al., “Changes in U.S. Family Finances from 2019 to 2022,” Federal Reserve Bulletin 2023, https://www.federalreserve.gov/publications/files/scf23.pdf

---

### Bourdieu’s capital framework (economic / cultural / social)

1. **Name:** Pierre Bourdieu, “The Forms of Capital” (1986) — economic, cultural, and social capital as convertible forms of accumulated labor.
2. **Type:** Capital-type framework (sociological; **not** a mobility elasticity).
3. **Operational definition (quoted, not quantified):** Capital “can present itself in three fundamental guises: as **economic capital**, which is immediately and directly convertible into money and may be institutionalized in the forms of property rights; as **cultural capital**, which is convertible, on certain conditions, into economic capital and may be institutionalized in the forms of educational qualifications; and as **social capital**, made up of social obligations (‘connections’), which is convertible, in certain conditions, into economic capital and may be institutionalized in the forms of a title of nobility.” Cultural capital: **embodied** (durable dispositions of mind and body), **objectified** (books, machines, pictures), **institutionalized** (educational qualifications).
4. **Data source:** None in the 1986 essay — it is a theoretical conversion of *Distinction* / field analysis, not a PSID regression. Later “cultural capital” survey indexes (e.g., parental books, museum visits) are **operationalizations by other authors**, not Bourdieu’s coefficient.
5. **Named finding:** There is **no** IGE-style number in “The Forms of Capital.” The claim is categorical: economism that counts only money-convertible practices is incomplete; conversion across forms is **costly and field-specific**. Educational qualifications are the institutionalized form of cultural capital, **not** Chetty’s college mobility **rate**.
6. **What this is NOT:** Not a competing estimate of ρ or β. Not “social capital” as in Chetty 2014’s Putnam-style CZ covariate. Not SCF net worth. Treating “cultural capital” as if it had a 0.34 rank-rank is a **category error**.
7. **Scope:** Analytic essay on capitalist societies’ fields of practice; no sample universe.
8. **Named case:** Institutionalized cultural capital = credentials — adjacent to, **not the same statistic as**, Mobility Report Cards’ bottom-quintile → top-quintile rates.
9. **Falsifier:** If “The Forms of Capital” stated a numerical US intergenerational elasticity for cultural capital, cell 5’s “no IGE-style number” would die. (It does not.)
10. **OPEN:** How to measure embodied cultural capital without collapsing it into years of schooling (itself already in the education-channel entry). Translation between Bourdieu and Chetty is **interpretive**, not a data merge.
11. **Sources:** Bourdieu, “The Forms of Capital,” in Richardson (ed.), *Handbook of Theory and Research for the Sociology of Education*, 1986; commonly cited English text https://web.stanford.edu/~eckert/PDF/Bourdieu1986.pdf

---

### Assortative mating (educational / income sorting)

1. **Name:** Educational (and income) **assortative mating** — who marries whom — as a household-level inequality and mobility confounder.
2. **Type:** Structural channel (marriage market) with quantitative decompositions.
3. **Operational definition:** Positive assortative mating = within-couple correlation of education (or earnings) above random matching. Inequality contribution: counterfactual **Gini** of household income under **random matching** vs observed matching. **Household** Chetty ranks already embed spouse income; individual ranks do not.
4. **Data source:**
   - Greenwood, Guner, Kocharkov, Santos, *AER* Papers & Proceedings (**P&P**) 104(5) 2014: US Census Bureau microdata (1960 vs 2005 matching).
   - **Corrigendum** (2015) to that paper’s Table 2.
   - Eika, Mogstad, Zafar, *JPE* 127(6) 2019: Denmark, Germany, Norway, United Kingdom, United States.
5. **Named finding:**
   - Greenwood et al. *AER* P&P 2014 **published abstract:** random matching in 2005 would cut Gini **0.43 → 0.34**. **Corrigendum 2015:** that counterfactual is wrong; random matching cuts 2005 Gini only **0.430 → 0.420**; forcing 1960 sorting on 2005 data cuts **0.430 → 0.429**. Rise in **singles** (marriage/divorce) still moves Gini (1960 data with 2005 single share: **0.342 → 0.382**).
   - Eika, Mogstad, Zafar *JPE* 2019: assortative mating accounts for a **non-negligible** share of **cross-sectional** household-income inequality in each country; **changes** in assortative mating over time “barely move” inequality **trends** (more sorting at low education offset by less sorting among college graduates). Returns to education, not sorting trends, drive much of the rise.
6. **What this is NOT:** Not IGE. Not Chetty individual-income ranks. Not Bourdieu’s social capital. **Do not** cite the 2014 abstract’s 0.43→0.34 after the corrigendum. Household-income mobility (Chetty family income) **already includes** spouse earnings — assortative mating is inside that Y, not an extra β to add.
7. **Scope:** Greenwood: US married couples, Census, 1960 and 2005. Eika et al.: five countries, education categories, household income. Neither is a parent–child wealth panel.
8. **Named case:** US 1960 vs 2005 (Greenwood, with corrigendum). Five-country cross-section vs trend (Eika et al.). Chetty race paper: household vs individual Black–white gap (13 vs 5 percentiles) is **partly a marriage-market fact** — adjacent, not a Gini decomposition.
9. **Falsifier:** If the corrigendum still reported a 9-point Gini drop from random matching in 2005, cell 5’s “0.430 → 0.420” would die. If Eika et al. found that *changes* in sorting explained most of the inequality trend, that named finding would die.
10. **OPEN:** Income-sorting vs education-sorting (different indices). Effects on **intergenerational** β when children’s Y is household income — Chetty uses family income by default; a full re-estimation on individual income plus spouse formation is **not** the Greenwood Gini exercise.
11. **Sources:** Greenwood, Guner, Kocharkov, Santos, *AER* 2014, 104(5): 348–353; Corrigendum, https://www.jeremygreenwood.net/papers/ggksPandPcorrigendum.pdf ; Eika, Mogstad, Zafar, *JPE* 2019, 127(6): 2795–2835.

---

**Not in this pass (do not invent):** occupation-class mobility tables (Erikson–Goldthorpe); sibling correlations as a separate heritability machine; Chetty “fading American dream” state-level 1984 micro cells not copied; Pfeffer–Killewald multigenerational wealth; NLSY-only IGE replications. Add later only with the named microdata.
