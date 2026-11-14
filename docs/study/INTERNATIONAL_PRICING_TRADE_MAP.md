# International Pricing & Trade Map

Descriptive / institutional reference. **Why the same good costs a different amount in different countries, and which named mechanism is doing it.** Not an econ-101 lecture and not a policy brief. Primary sources first. Wikipedia is a finding aid. OPEN rather than invented. Pull date **2026-11-14**. Companion to the Atlas and the Religion / Standards / War / Class maps — **not** the same field grid. Standing rules: [`docs/study/STUDY_SERIES_RULES.md`](STUDY_SERIES_RULES.md).

Do not mash machines. A **VAT** (value-added tax) is not a tariff. A **PPP** (purchasing-power parity) conversion factor is not the market exchange rate. Steam’s purchasing-power *tool* is not a World Bank income-group mandate. **EU** (European Union) regional exhaustion is not the **US** (United States) first-sale doctrine. Incomplete pass-through is not “the price moved 1:1 with the dollar.”

---

## How to read an entry

Every entry uses the same fixed **11-field** template. Field labels stay in this form throughout. In any **Falsifier** line, “cell N” means field N on this list (so “cell 6” is Named/quantified case).

1. **Mechanism/concept name**
2. **Type** — tax/tariff instrument / pricing policy / legal framework / contractual practice / macroeconomic adjustment
3. **Legal or economic basis** — statute, formula, or documented practice
4. **Who sets it** — the specific actor
5. **What creates the differential** — the causal mechanism in the actor’s own terms
6. **Named/quantified case** — a dated, sourced comparison, not a vibe
7. **What this is NOT** — the adjacent, frequently-confused mechanism
8. **Scope** — goods, regions, years
9. **Falsifier** — the fact that would disprove cell 6
10. **OPEN** — disputed figures, pending litigation, unclear current status
11. **Primary sources**

---

### Purchasing-power parity conversion (ICP (International Comparison Program) / IMF (International Monetary Fund)) and the Big Mac Index

1. **Name:** **PPP** conversion factors from the ICP, used by the **World Bank** and IMF **WEO** (*World Economic Outlook*); plus *The Economist* **Big Mac Index** (1986–) as a one-good, tax-inclusive burger PPP.
2. **Type:** Macroeconomic adjustment (statistical conversion), not a tax and not a posted store price.
3. **Legal or economic basis:** ICP: comparable prices × national-accounts expenditures → regional PPPs → global PPPs linked to the United States as base (World Bank ICP 2021 methodology). IMF WEO: starts from ICP 2017–21 PPPs, then extends non-survey years by relative **GDP** (gross domestic product) deflators (country deflator ÷ US deflator). Big Mac: implied exchange rate = local burger price / US burger price; undervaluation = implied vs actual market rate. *The Economist*: “never intended as a precise gauge.”
4. **Who sets it:** ICP Global Office at the World Bank (with regional agencies, **OECD** (Organisation for Economic Co-operation and Development), Eurostat). IMF Research Department publishes WEO implied PPP rates. Big Mac: *The Economist* data team from McDonald’s prices (US price McDonald’s-provided since July 2022), **LSEG** (London Stock Exchange Group) Workspace foreign-exchange rates, IMF GDP for the gourmet/GDP-adjusted variant.
5. **What creates the differential:** A PPP rate is the units of local currency needed to buy the same basket as one international dollar. It is **constructed** so that real volumes can be compared. It does **not** move a checkout price. The Big Mac version uses one standardized sandwich, **including tax**.
6. **Named/quantified case:** *The Economist* Big Mac raw index, observation date **2026-07-01** (GitHub `big-mac-raw-index.csv`): United States **US$6.22**; Switzerland **CHF 7.30** (**US$9.04** at 0.80735 CHF/USD) — Swiss burger **~45%** above the US dollar price; India **₹236.25** (**US$2.45**) — **~61%** below. Britain **£5.49** (**US$7.40**). All prices tax-inclusive per the index note. These are **burger prices**, not ICP GDP PPPs.
7. **What this is NOT:** Not the market exchange rate used at the register. Not a tariff. Not Steam’s multi-variable conversion tool (that is a platform pricing policy). Not VAT-inclusive vs exclusive display rules. Do **not** report India’s Big Mac dollar price as India’s ICP household-consumption PPP.
8. **Scope:** ICP: GDP and expenditure components, reference years 2011/2017/2021, participating economies; non-participants imputed. Big Mac: McDonald’s markets in the index; not a full consumption basket; not every country.
9. **Falsifier:** If the 2026-07-01 comma-separated data file listed the US Big Mac at US$9.04 and Switzerland at US$6.22, cell 6 dies. If IMF WEO stated it used only market foreign-exchange rates, not ICP-extended deflators, cell 3 dies.
10. **OPEN:** Latest ICP 2021 country-level World Bank indicator `PA.NUS.PPP` table not copied this pass (data request timed out). GDP-adjusted Big Mac vs raw index are **two** *Economist* series — do not mash. Lebanon and other dual-rate cases are flagged in *Economist* sources, not resolved here.
11. **Sources:** World Bank ICP 2021 methodology, https://www.worldbank.org/en/brief/2021/04/30/icp2021-methodology-o ; IMF WEO frequently asked questions, https://www.imf.org/en/publications/weo/frequently-asked-questions ; *The Economist* Big Mac index, last updated 30 July 2026, https://www.economist.com/interactive/big-mac-index ; data https://github.com/TheEconomist/big-mac-data

---

### VAT and sales-tax differentials (display-inclusive vs exclusive)

1. **Name:** EU **VAT** rates under Council Directive **2006/112/EC**, plus US retail **sales tax** (California statewide base as the named US machine).
2. **Type:** Tax instrument + consumer-display rule.
3. **Legal or economic basis:** Directive 2006/112/EC Art. 1: VAT is a general tax on consumption, proportional, deducted along the chain, applied through retail. Art. 97: “The standard rate shall not be lower than **15 %**.” No EU maximum. Member States set the number and level of rates. **Directive 98/6/EC** Art. 2–3: the “selling price” shown to consumers is the **final** price **including VAT and all other taxes**. California: statewide sales-and-use tax **7.25%** (Rev. & Tax. Code §§ 6051, 6201 and listed add-ons); **CDTFA** (California Department of Tax and Fee Administration) — tax is **added** to the pre-tax price (tax-exclusive shelf).
4. **Who sets it:** EU: each Member State’s legislature within the Directive; Commission **TEDB** (Taxes in Europe Database) republishes member-notified rates. US: state legislatures + local district taxes; California CDTFA administers.
5. **What creates the differential:** Different statutory rates **and** whether the posted number already contains the tax. A Hungarian shelf price is VAT-in; a California shelf price is typically VAT/sales-tax-out. Comparing a Hungarian sticker to a California sticker without reversing the tax is a **display** error, not a tariff.
6. **Named/quantified case:** Your Europe VAT table (EU official consumer/business portal): standard rates **Hungary 27%**, **Luxembourg 17%**. On a **€100** net (tax-exclusive) supply of a standard-rated good: Hungary **€127** vs Luxembourg **€117** — a **10 percentage-point** statutory gap, **€10** on that net. California statewide base: **$100** taxable item → **$7.25** tax → **$107.25** (before district add-ons of 0.10–2.00%). Sources: https://europa.eu/youreurope/business/finance-and-tax/vat/vat-rules-rates/index_en.htm ; https://cdtfa.ca.gov/taxes-and-fees/sut-rates-description.htm
7. **What this is NOT:** Not an import **tariff** (next entry). Not PPP. Not geo-blocking. Do not treat Hungary 27% vs California 7.25% as a 19.75-point “same tax” — one is a multi-stage VAT on a tax-inclusive display, the other is a single-stage retail tax on a tax-exclusive display, with different bases (services coverage, exemptions).
8. **Scope:** VAT: intra-EU supplies of goods/services as defined in the Directive; reduced/super-reduced/parking rates are **other** columns. Sales tax: California tangible personal property; food/prescription exemptions exist (CDTFA Pub. 61) — do not apply 7.25% to exempt food.
9. **Falsifier:** If Art. 97 set a 27% EU-wide standard rate, the Hungary/Luxembourg gap dies. If CDTFA’s statewide base were not 7.25%, cell 6’s $107.25 arithmetic dies.
10. **OPEN:** Live TEDB rates move (Estonia, Finland in the Your Europe table already differ from some 2024 secondary tables). District California totals by address — **look up**, don’t invent a city rate. Digital business-to-consumer VAT place-of-supply (One Stop Shop) is a **separate** machine.
11. **Sources:** Directive 2006/112/EC Arts. 1, 97 (consolidated); Directive 98/6/EC Arts. 2–3; Commission VAT rates page, https://taxation-customs.ec.europa.eu/taxation/vat/vat-directive/vat-rates_en ; CDTFA statewide 7.25% breakdown.

---

### Import tariffs (named HTS line)

1. **Name:** US **HTS** (Harmonized Tariff Schedule) Column 1 general (**MFN** (most-favoured-nation)) duty on a specified **HS** (Harmonized System) subheading, as published by the **USITC** (United States International Trade Commission).
2. **Type:** Tax/tariff instrument.
3. **Legal or economic basis:** HTS implemented under 19 **U.S.C.** (United States Code) § 1202; classification by General Rules of Interpretation. Duty is generally **ad valorem** on customs value. Chapter 99 can **add** Section 232/301/other remedies on top of the Chapter 1–97 rate — those are **separate** lines, not the Column 1 rate.
4. **Who sets it:** Congress (statute / trade-agreement implementing bills); USITC maintains the HTS; **CBP** (U.S. Customs and Border Protection) assesses at entry; the President may add Chapter 99 remedies under delegated statutes.
5. **What creates the differential:** The importer of record pays the duty; it enters the landed cost. A 25% Column 1 rate on trucks is not a 25% VAT. Preferential **FTA** (free-trade agreement) Column 1 “Special” rates can be **Free** if origin rules are met (see USMCA entry).
6. **Named/quantified case:** **HTS 8704.21.01** — motor vehicles for the transport of goods, compression-ignition, **G.V.W.** (gross vehicle weight) not exceeding 5 metric tons (the light-truck / “chicken tax” line). USITC Chapter 87, **2026 HTS Rev. 21**: Column 1 general **25%**; Special **Free** for listed FTA/preference program symbols in the HTS (A+, AU, B, BH, CL, CO, D, E, IL, JO, MA, OM, P, PA, PE, S, SG); **25% (KR)**. Contrast passenger cars **8703.23.01** (1,500–3,000 cc spark-ignition): Column 1 general **2.5%** (2024 HTS Rev. 10 Chapter 87 dump). **Do not** add Section 232/301 on top of 25% unless quoting a Chapter 99 heading for a named origin and date — those stack **OPEN** as of this pull.
7. **What this is NOT:** Not VAT. Not PPP. Not Steam regional pricing. A USMCA **originating** truck that enters **Free** is not “the chicken tax went away for the world” — it went away **for originating goods**.
8. **Scope:** Goods classified in that subheading, entered into the US customs territory. Rates are **revision-dated**; always name the HTS release.
9. **Falsifier:** If USITC Chapter 87 for 8704.21.01 showed Column 1 general **2.5%**, cell 6 dies. If 8703.23.01 general were 25%, the car/truck contrast dies.
10. **OPEN:** Section 232 auto/light-truck Chapter 99 add-ons (CBP frequently asked questions; stacking by origin) — **do not** invent a single “total rate for Mexico.” Korea’s Special 25% on 8704.21.01 vs Free on many other partners is in the HTS text; legal history OPEN this pass.
11. **Sources:** USITC Chapter 87, https://hts.usitc.gov/reststop/file?filename=Chapter+87&release=2026HTSRev21 (8704.21.01); 2024HTSRev10 (8703.23.01 2.5%).

---

### Platform regional pricing (Steam vs consoles)

1. **Name:** **Steam** (Valve) regional/currency pricing tools; contrasted with **PlayStation** Store country/region lock.
2. **Type:** Pricing policy (platform + publisher), not a public-law tariff.
3. **Legal or economic basis:** Steamworks documentation: partners **set** prices in **37 currencies** and **4 region groups** (`USD_CIS`, `USD_LATAM`, `USD_MENA`, `USD_SASIA`). Optional converters: (1) exchange-rate only; (2) **purchasing-power conversion only** — “public data about the purchasing power of customers within a given country and/or region”; (3) **multi-variable** — local purchasing power, expected cost of comparable entertainment goods, **and** exchange rate. Valve reviews proposed prices. Minimum base ≥ multi-variable conversion of **$0.99 USD**. Steam displays tax per “expected local norms” (Steamworks Tax frequently asked questions). PlayStation: account **country/region cannot be changed** after creation; Store content and voucher codes are region-matched (Sony support).
4. **Who sets it:** Steam: the **partner who gets paid** (publisher/developer with “Manage pricing and discounts”), subject to Valve review — **not** an automatic World Bank table. PlayStation: Sony Interactive Entertainment storefront per country; publishers submit prices into Sony’s pipeline (Sony does not publish an equivalent three-method converter).
5. **What creates the differential:** On Steam, a **chosen** local price (or a chosen converter applied to a USD point), plus tax-display norms, plus region-group USD discounts where there is no local currency. On PlayStation, a **region-locked catalog** so the customer cannot check out the other storefront on that account.
6. **Named/quantified case:** Steamworks, pull **2026-11-14**: documentation of 37 currencies / 4 region groups and three named converters; conversion tables “public data as of **October 2026**” (Steamworks pricing explorer). **Not** a claim that Valve uses World Bank **income-group** classifications — that classification exists (Atlas **GNI** (gross national income), 1 July each year) but **Steamworks does not name it**. PlayStation: Sony, “Once created, your country/region can’t be changed” — https://www.playstation.com/en-us/support/account/check-account-country-region/
7. **What this is NOT:** Not foreign-exchange pass-through of a single global USD price (that is converter #1 only, and only if the partner picks it). Not PPP/ICP. Not VAT (tax is a display layer on top). Not geo-blocking Regulation 2018/302 (Steam is not an EU statute). **Do not** attribute a Brazilian Steam price to “the real weakened” if the partner set a purchasing-power or multi-variable price.
8. **Scope:** Steam packages (store SKUs); microtransactions/subscriptions have other docs. PlayStation Store digital; physical disc region is a **license** fact (Sony: add-on region must match disc).
9. **Falsifier:** If Steamworks required partners to use World Bank income groups and forbade custom per-currency prices, cell 3/4 die. If Sony allowed post-creation country changes as a normal self-serve, cell 6’s PlayStation lock dies.
10. **OPEN:** The exact public dataset behind Steam “purchasing power” (ICP? Big Mac? other) — **not named** in the pricing doc. Xbox Store algorithm similarly unpublished. Third-party store scrapes (PlatPrices, SteamDB) are **not** Valve/Sony primary — do not paste their USD gaps as official.
11. **Sources:** https://partner.steamgames.com/doc/store/pricing ; https://partner.steamgames.com/doc/store/pricing/currencies ; PlayStation country/region support page above.

---

### Grey market / parallel imports (exhaustion vs first sale)

1. **Name:** Parallel trade in genuine goods: **EU/EEA** (European Economic Area) **regional exhaustion** of trade-mark rights vs US copyright **first-sale** doctrine (**Kirtsaeng**).
2. **Type:** Legal framework.
3. **Legal or economic basis:**
   - EU trade marks: Directive **2015/2436** Art. 15 (successor to 89/104 Art. 7): rights exhaust when goods are put on the market **in the EEA** by the proprietor or with consent; proprietor may still oppose further commercialisation if condition is changed/impaired. **Silhouette** C-355/96 (16 July 1998): Member States **may not** adopt **international** exhaustion for extra-EEA first sales.
   - US copyright: 17 U.S.C. **§ 109(a)** — owner of a copy “**lawfully made under this title**” may sell that copy without the copyright owner’s authority. **Kirtsaeng v. John Wiley & Sons**, **568 U.S. 519** (2013): that includes copies **lawfully made abroad**. § 602(a)(1) importation right is limited by § 109 (*Quality King*, 523 U.S. 135, was US-made goods on a round trip; *Kirtsaeng* extended to foreign manufacture).
4. **Who sets it:** Court of Justice of the EU (Silhouette); US Supreme Court (Kirtsaeng); legislatures wrote the Directive / Copyright Act.
5. **What creates the differential:** A publisher/brand can **price Asia below the US** and still, in the US, face lawful **resale** of those copies (*Kirtsaeng*). The same brand can often **block** extra-EEA grey imports **into** the EEA (*Silhouette*), while **intra-EEA** parallel trade is the point of regional exhaustion.
6. **Named/quantified case:** *Kirtsaeng*: Wiley Asia English textbooks marked not to be taken into the US; student had friends buy them in **Thai** shops and resell in the US; trial **$600,000** statutory damages, reversed. Holding: first sale applies to foreign-made authorized copies. *Silhouette*: unused Silhouette frames first marketed **outside** the EEA, then offered in Austria by Hartlauer — proprietor could oppose; international exhaustion incompatible with the Directive.
7. **What this is NOT:** Not counterfeiting (goods are genuine). Not VAT. Not Steam account-region policy (contract / terms of service, often no “copy” sold). Not geo-blocking Regulation 2018/302. US **trade-mark** grey-market rules (e.g. *Lever* / material-difference line) are a **third** machine — not mashed with § 109.
8. **Scope:** Physical copies (books, branded goods). Digital downloads: **OPEN** whether a “license” is a § 109 “copy” (*UsedSoft* C-128/11 is EU software; US *Vernor v. Autodesk* is license-not-sale).
9. **Falsifier:** If *Kirtsaeng* had held § 109 geographically limited to US manufacture, cell 6’s Thai-book resale holding dies. If *Silhouette* had required international exhaustion, cell 3 dies.
10. **OPEN:** Patent exhaustion (*Impression Products v. Lexmark*, 581 U.S. 118 (2017)) is parallel but not this cell. Post-*Kirtsaeng* contractual/license attempts to recreate territorial walls — fact-specific.
11. **Sources:** Directive 2015/2436 Art. 15; Case C-355/96 *Silhouette*, **ECLI** (European Case Law Identifier):EU:C:1998:374, https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:61996CJ0355 ; 17 U.S.C. §§ 109(a), 602(a)(1); *Kirtsaeng*, 568 U.S. 519, https://www.law.cornell.edu/supremecourt/text/11-697

---

### Geo-blocking and price-discrimination law (EU 2018/302 vs no US equivalent)

1. **Name:** Regulation **(EU) 2018/302** (Geo-blocking Regulation), 28 Feb 2018, **OJ** (*Official Journal of the European Union*) L 60I, 2.3.2018, p. 1; applied 3 Dec 2018. No US federal counterpart of that scope.
2. **Type:** Legal framework (internal-market discrimination), **not** a price-harmonization statute.
3. **Legal or economic basis:** Art. 3: no blocking/limiting access to an online interface, and no redirect without **explicit consent**, for reasons of nationality, residence, or establishment. Art. 4: no different **general conditions of access** in three situations — (a) goods delivered/collected where the trader already offers that; (b) electronically supplied services **other than** copyright-protected works/subject matter; (c) services received in a physical place in a Member State where the trader operates. Art. 4(2): traders **may** still offer different net sale prices by Member State or customer group on a **non-discriminatory** basis. Recital/Commission Q&A: **no duty to deliver cross-border** if not already offered; **no duty to equalize prices**. Copyrighted digital content is **carved out** of Art. 4(1)(b).
4. **Who sets it:** European Parliament and Council; enforcement by Member State authorities designated under the Regulation; Commission questions-and-answers (**Q&A**) (REV2, 26 May 2020) as administrative guidance, not the Regulation.
5. **What creates the differential:** The Regulation attacks **access discrimination** (you may not be blocked from seeing the German shop). It **does not** force the German shop’s euro price onto a French customer if the trader’s published conditions lawfully differ — and it **does not** open Netflix-style catalogues.
6. **Named/quantified case:** Statutory text, not a scraped price: Art. 4(2) expressly preserves territorial price lists. Commission summary: “does not oblige traders to deliver across borders … or to harmonise prices.” US: no analogous federal ban on blocking a .com storefront by billing **ZIP** (Zone Improvement Plan) Code; platform terms of service and state consumer law are **other** machines.
7. **What this is NOT:** Not VAT. Not tariff. Not exhaustion (*Silhouette*). Not a most-favoured-customer clause. Not “the EU banned regional game prices” — games as copyrighted digital content sit in the Art. 4(1)(b) **exclusion**.
8. **Scope:** Traders selling to consumers/business customers in the EU/EEA as defined; audiovisual services largely outside. Applies among Member States, not EU-vs-US checkouts.
9. **Falsifier:** If Art. 4 required a single EU-wide net price, cell 5/6 die. If Art. 4(1)(b) covered copyrighted e-books/games, the carve-out claim dies.
10. **OPEN:** Commission review of extending the Regulation to copyrighted content — political, not in force as a rewrite of Art. 4(1)(b) this pass. Private enforcement volume.
11. **Sources:** Regulation (EU) 2018/302, https://eur-lex.europa.eu/eli/reg/2018/302/oj/eng ; Commission Q&A REV2, https://commission.europa.eu/system/files/2020-05/geoblocking_en.pdf

---

### Currency exchange-rate pass-through (incomplete)

1. **Name:** Exchange-rate **pass-through** into import (and, separately, consumer) prices — the elasticity of local-currency prices with respect to the exchange rate.
2. **Type:** Macroeconomic adjustment (empirical regularity), not a statute.
3. **Legal or economic basis:** No legal mandate. Empirical: Campa & Goldberg, “Exchange Rate Pass-Through into Import Prices,” **REStat** (*Review of Economics and Statistics*) 87(4) 2005. Gopinath, Itskhoki, Rigobon, “Currency Choice and Exchange Rate Pass-Through,” **AER** (*American Economic Review*) 100(1) 2010 — pass-through **conditional on a price change**, split by invoice currency.
4. **Who sets it:** Exporters/importers choosing invoice currency and reset frequency; not a finance ministry foreign-exchange “pass-through order.”
5. **What creates the differential:** If pass-through is **incomplete**, a 10% depreciation does **not** raise import prices 10% in one quarter. Local-currency pricing, invoicing in dollars, and sticky prices break 1:1.
6. **Named/quantified case:** Campa & Goldberg (2005), 23 **OECD** countries, quarterly 1975–2003: unweighted average pass-through into **import prices** ~**46%** in one quarter, ~**64%** longer-run; **United States** ~**25%** short-run, ~**40%** longer-run; **Germany** ~**60%** / ~**80%**. Gopinath, Itskhoki, Rigobon (2010), US import micro data: even **conditional on a price change**, dollar-invoiced goods ~**25%** pass-through vs non-dollar ~**95%**.
7. **What this is NOT:** Not PPP (a constructed conversion). Not a tariff. Not Steam converter #1 unless the partner actually chose foreign-exchange-only and resets continuously — they usually don’t. **Import-price** pass-through is **not** **CPI** (consumer price index) pass-through (the latter is typically smaller; do not mash).
8. **Scope:** Campa–Goldberg: custom import-price indexes, OECD, through 2003. Gopinath et al.: US imports with observed currency. Later samples **OPEN**.
9. **Falsifier:** If Campa–Goldberg’s OECD short-run average were 100%, “incomplete” in cell 6 dies. If Gopinath et al. found 25% for **non-dollar** invoices, the currency-split finding dies.
10. **OPEN:** Whether US short-run 25% still holds post-2003 / post-invoice-currency shifts. Pass-through into **retail** shelves vs border import prices.
11. **Sources:** Campa & Goldberg, *REStat* 2005, 87(4): 679–690, and Federal Reserve Bank of New York manuscript https://www.newyorkfed.org/medialibrary/media/research/economists/goldberg/passthrough093004.pdf ; Gopinath, Itskhoki, Rigobon, *AER* 2010, 100(1): 304–336.

---

### Free-trade agreements and origin schedules (USMCA autos)

1. **Name:** **USMCA** (United States–Mexico–Canada Agreement) preferential **0%** for **originating** vehicles, gated by a **phased RVC** (regional value content) schedule — not a phase-down of the MFN rate itself.
2. **Type:** Legal framework (treaty origin rules + tariff preference).
3. **Legal or economic basis:** USMCA Chapter 4; Appendix to Annex 4-B (autos). International Trade Administration: qualifying goods that were zero under **NAFTA** (North American Free Trade Agreement) **remain zero**. Passenger vehicles / light trucks **RVC** (net cost method): **66%** from **1 July 2020**, **69%** 1 July 2021, **72%** 1 July 2022, **75%** from **1 July 2023**. Heavy trucks: 60% (2020) → 64% (2024) → 70% (2027). Additional: **LVC** (labor value content) 40–45% at ≥ **US$16**/hour; **70%** North American steel and aluminum purchases. Non-originating vehicles pay HTS Column 1 (e.g. 2.5% cars / 25% light trucks) **plus** any Chapter 99.
4. **Who sets it:** The three Parties (treaty); US implementing legislation / HTS General Note 11; CBP origin verification.
5. **What creates the differential:** Two trucks that look the same at the border: one **originating** → **Free**; one not → **25%** (8704.21.01) before remedies. The 2020–23 calendar is a **tightening of origin**, not a sliding MFN duty.
6. **Named/quantified case:** **ITA** (International Trade Administration) USMCA Auto Report: RVC steps 66/69/72/**75%** net cost for passenger vehicles and light trucks; USMCA in force **1 July 2020**. Same page: NAFTA-zero goods stay zero **if they still originate**.
7. **What this is NOT:** Not VAT. Not a promise that Mexican-built pickups are duty-free regardless of content. Not Campa–Goldberg pass-through. Do not call the 66→75 path a “tariff phase-out from 25% to 0%.”
8. **Scope:** Automotive goods in the Autos Appendix; other chapters have other **PSRs** (product-specific rules). Steel/aluminum and LVC are **additional** origin tests, not tariff lines.
9. **Falsifier:** If the Autos Appendix required 75% RVC on 1 July 2020 with no steps, cell 6’s schedule dies. If originating USMCA light trucks still paid the 25% Column 1 rate, the preference claim dies.
10. **OPEN:** Dispute-settlement over tracing/core parts (US–Mexico auto **ROO** (rules of origin) panel) — legal characterization **OPEN**. Interaction with 2025–26 Section 232 auto proclamations for USMCA partners — quote CBP/Chapter 99, don’t guess a net rate.
11. **Sources:** https://www.trade.gov/usmca-auto-report ; USMCA Chapter 4 PDF, https://ustr.gov/sites/default/files/files/agreements/FTA/USMCA/Text/04-Rules-of-Origin.pdf ; HTS 8704.21.01 (prior entry).

---

### Regional distribution / territorial licensing

1. **Name:** Territorial exclusive licenses that **contractually** wall a catalog or SKU by country, independent of tax and tariff.
2. **Type:** Contractual practice (plus copyright’s territoriality).
3. **Legal or economic basis:** Copyright is territorial; a US owner may assign **Wiley Asia** the right to print/sell **outside** the US (*Kirtsaeng* facts: foreign editions “not to be taken into the United States”). Steam: missing a currency **makes the game unavailable** in that currency’s countries (Steamworks frequently asked questions) — a **package** configuration, not a customs duty. Sony: voucher/disc **region must match** the account; “Content and services available on PlayStation Store vary by country/region.”
4. **Who sets it:** Rights holder / exclusive licensee / platform package configuration (Valve partner; Sony storefront).
5. **What creates the differential:** The customer **cannot buy** the cheaper foreign SKU on that account even if exhaustion would allow resale of a **physical** copy. Digital “license not sale” is how many **EULAs** (end-user license agreements) try to stay outside § 109.
6. **Named/quantified case:** *Kirtsaeng* record: Wiley’s foreign textbooks carried a **geographic** legend and a lower Thai retail price than the US edition — that price gap was a **license territory**, later attacked by physical parallel import (first-sale entry). Steamworks: “if you do not have a price entered for Japanese Yen, then users located in Japan will be unable to purchase your game.”
7. **What this is NOT:** Not VAT, not HTS, not 2018/302 (and 2018/302 **excludes** this class of copyrighted digital services). Not PPP. Exhaustion may defeat the wall for **physical** copies in the US; it does **not** automatically open a Japanese Steam SKU.
8. **Scope:** Publishing, games, video-on-demand windows. Sports territorial broadcasting is adjacent, not copied here.
9. **Falsifier:** If Steamworks filled missing JPY from USD automatically and still sold in Japan, cell 6’s unavailability rule dies. If Wiley’s Asian editions had no territorial legend and the same US list price, that named case’s contractual wall dies.
10. **OPEN:** Enforceability of digital license-not-sale after *Kirtsaeng* / *UsedSoft*. Which PlayStation SKUs are publisher-local vs foreign-exchange-converted — Sony does not publish the split.
11. **Sources:** *Kirtsaeng*, 568 U.S. 519; Steamworks Pricing frequently asked questions (missing currencies); PlayStation country/region support page.

---

### Resale price maintenance across borders

1. **Name:** **RPM** (resale price maintenance) — manufacturer-imposed **minimum/fixed** resale prices, and the **split** between US federal antitrust after *Leegin* and EU **hardcore** treatment.
2. **Type:** Legal framework (antitrust) constraining a contractual practice.
3. **Legal or economic basis:**
   - US: *Leegin Creative Leather Products, Inc. v. PSKS, Inc.*, **551 U.S. 877** (2007) — minimum RPM is **not** per se illegal under Sherman Act § 1; **rule of reason**. (**CRS** (Congressional Research Service) RS22700 summary of the holding.)
   - EU: Regulation **(EU) 2022/720** (Vertical Block Exemption), Art. **4(a)**: exemption **does not apply** to agreements that restrict the buyer’s ability to determine its sale price; **maximum** or **recommended** prices OK unless pressure/incentives make them **fixed/minimum**. Art. 101 **TFEU** (Treaty on the Functioning of the European Union) still applies individually.
4. **Who sets it:** US: Supreme Court (standard of review); **DOJ** (Department of Justice) / **FTC** (Federal Trade Commission) / private plaintiffs enforce. EU: Commission and national competition authorities; 2022/720 is Council/Commission regulation.
5. **What creates the differential:** A US supplier **may try** to hold a floor under rule-of-reason (state *Leegin*-repealer statutes **OPEN**). The same supplier **cannot** rely on the EU block exemption for a minimum internet price across Member States; **MAP** (minimum advertised price) that blocks discount advertising can be treated as hardcore (2022 Guidelines). Cross-border RPM therefore **breaks** at the EU edge even if US counsel signed off.
6. **Named/quantified case:** *Leegin* (2007): Brighton leather goods; Court 5–4 overruled *Dr. Miles* (1911) per se rule. EU: Regulation 2022/720 Art. 4(a) text (in force; replaced 330/2010). No single euro fine is copied here without a named Commission decision docket.
7. **What this is NOT:** Not a tariff. Not VAT. Not geo-blocking (2018/302 Art. 4(2) even **allows** different list prices). Not Steam’s **own** price (Valve is the storefront; RPM is **manufacturer vs distributor**). Recommended retail price ≠ RPM unless enforced.
8. **Scope:** Vertical agreements. Agency (no distributor risk) is outside 101(1) in EU guidance — **another** characterization. Online intermediation services are **suppliers** under 2022/720, so a platform-imposed floor on merchants is Art. 4(a).
9. **Falsifier:** If *Leegin* had kept per se illegality, cell 3’s US standard dies. If 2022/720 Art. 4(a) exempted minimum RPM, the EU hardcore claim dies.
10. **OPEN:** Which US **states** still treat minimum RPM as per se under state antitrust. Individual EU Art. 101(3) justifications for RPM (Guidelines admit rare efficiencies) — case-by-case. Commission fines in specific game/console RPM cases not docketed this pass.
11. **Sources:** *Leegin*, 551 U.S. 877; Regulation (EU) 2022/720 Art. 4(a), https://eur-lex.europa.eu/eli/reg/2022/720/oj/eng

---

**Not in this pass (do not invent):** anti-dumping / **CVD** (countervailing duty) margins; Section 301 list totals by origin; Apple App Store commission as a price wedge; pharmaceutical reference pricing / **TRIPS** (Agreement on Trade-Related Aspects of Intellectual Property Rights); carbon border adjustment. Add later only with the named instrument text.
