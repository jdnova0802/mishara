# PASTE — Issuing batch (settled 11 Oct 2026)

SEND Tuesday 2026-10-13. Monday 2026-10-12 stays the VAMP/ECM batch. Do not add these to that send.

Cold price is the existing monthly floor: **$5,000 the month a live card authorization hits the mouth and comes back AUTHORIZE or DECLINE.** If none hits, no invoice. The $25,000 weld and the 10 basis points stay off this email. They are the register after a month of cleared volume, if the desk asks. The Sept 26 line of $5,000 plus about 1% was an illustration. It is not this price.

The mouth is already live: `POST https://gate.velaru.xyz/v1/issuing/authorization` on Stripe `issuing_authorization.request`, under 2 seconds. Page: https://gate.velaru.xyz/issuing-mouth. Gate does not hold the card float.

Public pages only. No guessed emails. No security@, press@, jobs@, or legal-notice addresses. Log the send in SENT_TALLY.md the same day.

---

FOLLOW-UP

| Day | Action | Count |
|-----|--------|-------|
| Tue 2026-10-13 | Send the 1 below | 1 |
| Mon 2026-10-19 | One bump if no reply. Do not bump on Fri 2026-10-16. That day is the VAMP bump. | up to 1 |

Bump body:
```
Following up once. The mouth is still https://gate.velaru.xyz/issuing-mouth. $5,000 the month a live card authorization comes back AUTHORIZE or DECLINE. If that is not your write, ignore.
```

---

CHEAT-SHEET

1. Catena (catena.com) — hello@catena.com, printed on the homepage. The page says agents pay by card, ACH, wire, and stablecoin. The card line is the one this mouth can answer.

---

DO NOT SEND

| Name | Why it died |
|------|-------------|
| Arcade.dev | www.arcade.dev/contact is a form. No email on that page. support@arcade.dev is on a different site, an HTML5 games page, not this company. Their product is tool governance, not a card authorization. |
| NewCore | sales@newcore.io is on newcore.com/get-in-touch. The product is human and agent identity. No card authorization on the site. |
| Prelude | prelude.so is phone, device, and signup trust. No email printed on the pages checked. No card authorization. |
| Trustap | marketing@trustap.com and jobs@trustap.com are on the contact page. support@trustap.com is in the terms. The product is escrow between a buyer and a seller, not a card authorization. |
| Causa Prima | The only email on causaprima.ai/imprint is security@causaprima.ai. That is a security queue. Their agents move invoices. This mouth does not. |
| ReFiBuy | refibuy.ai/terms prints legalnotices@refibuy.ai for legal notices. No sales address on the site. The product is SKU visibility in shopping agents. |
| Limy | answers@limy.ai is on limy.ai/contact-us. The product is brand visibility in AI search. No card authorization. |
| AgentMail | contact@agentmail.cc and support@agentmail.cc are on agentmail.to. The product is an inbox for agents. No card authorization. |
| Runlayer | hello@mail.runlayer.com is in the homepage organization markup, not printed on the page. The product is MCP governance. No card authorization. |
| GitGuardian | Code-security company. No card-authorization product, and no send without an address printed for this ask. |
| Nava | nava.com is an AI cloud platform. docs.nava.com prints support@nava.com. No card authorization. |

---

EMAIL 1 — Catena

To: hello@catena.com
Subject: Catena — a card charge is the write

Body:
```
For the payments desk, Catena.
Nisaba LLC.

Your page says agents pay by card. That charge is the irreversible write. The mouth answers AUTHORIZE or DECLINE in under 2 seconds.
https://gate.velaru.xyz/issuing-mouth

$5,000 the month a live authorization from your card hits that URL and comes back. If none hits, no invoice.
```
