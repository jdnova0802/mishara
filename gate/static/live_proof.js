/**
 * Client-side live-state widgets. Same Merkle fold as evidence_log.verify_inclusion.
 * Reads public JSON only. Does not call /v1/seal as the proof.
 */
(function () {
  "use strict";

  function hexToBytes(hex) {
    var clean = String(hex || "").trim();
    if (!clean || clean.length % 2) throw new Error("bad_hex");
    var out = new Uint8Array(clean.length / 2);
    for (var i = 0; i < out.length; i++) {
      out[i] = parseInt(clean.substr(i * 2, 2), 16);
      if (Number.isNaN(out[i])) throw new Error("bad_hex");
    }
    return out;
  }

  function bytesToHex(bytes) {
    var s = "";
    for (var i = 0; i < bytes.length; i++) s += bytes[i].toString(16).padStart(2, "0");
    return s;
  }

  async function sha256(bytes) {
    var digest = await crypto.subtle.digest("SHA-256", bytes);
    return new Uint8Array(digest);
  }

  async function concatHash(a, b) {
    var both = new Uint8Array(a.length + b.length);
    both.set(a, 0);
    both.set(b, a.length);
    return sha256(both);
  }

  /** RFC-9162-shaped fold: even idx hash(leaf||sib), odd idx hash(sib||leaf). */
  async function verifyInclusion(leafHash, rootHash, proof) {
    var h = hexToBytes(leafHash);
    var idx = (proof && proof.index) || 0;
    var siblings = (proof && proof.siblings) || [];
    for (var i = 0; i < siblings.length; i++) {
      var sib = hexToBytes(siblings[i]);
      if (idx % 2 === 0) h = await concatHash(h, sib);
      else h = await concatHash(sib, h);
      idx = Math.floor(idx / 2);
    }
    return bytesToHex(h) === String(rootHash || "").toLowerCase();
  }

  function shortHash(value) {
    var h = String(value || "");
    if (h.length <= 18) return h || "—";
    return h.slice(0, 10) + "…" + h.slice(-6);
  }

  function parseIso(value) {
    if (!value) return NaN;
    var text = String(value);
    if (text.endsWith("Z") || /[+-]\d\d:\d\d$/.test(text)) return Date.parse(text);
    return Date.parse(text + "Z");
  }

  function clockIsLate(clock, now) {
    if (!clock || clock.disposition !== "open") return false;
    var due = parseIso(clock.due_at);
    return !Number.isNaN(due) && now > due;
  }

  function actWord(receipt, inclusionOk, now) {
    if (!inclusionOk) return "BROKEN";
    var canonical = (receipt && receipt.canonical_receipt) || {};
    var clock = canonical.clock || null;
    if (clockIsLate(clock, now)) return "LATE";
    var decision = String((receipt && receipt.decision) || "").toUpperCase();
    if (["AUTHORIZE", "GO", "ALLOW", "LIVE", "CLEAR", "PASS"].indexOf(decision) >= 0) {
      return "AUTHORIZE";
    }
    if (["DECLINE", "BLOCK", "DENY", "DENIED", "DEAD", "NO_GO", "HALT", "NO"].indexOf(decision) >= 0) {
      return "DECLINE";
    }
    return "HOLDS";
  }

  function setText(el, text) {
    if (el) el.textContent = text;
  }

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function formatRemain(ms) {
    if (ms <= 0) return "0:00";
    var s = Math.floor(ms / 1000);
    var h = Math.floor(s / 3600);
    var m = Math.floor((s % 3600) / 60);
    var sec = s % 60;
    if (h > 0) return h + ":" + pad2(m) + ":" + pad2(sec);
    return m + ":" + pad2(sec);
  }

  async function lookupReceipt(id) {
    var proofUrl = "/.well-known/receipt/" + encodeURIComponent(id) + "/proof.json";
    var receiptUrl = "/.well-known/receipt/" + encodeURIComponent(id) + ".json";
    var headUrl = "/.well-known/evidence-head.json";
    var proofRes = await fetch(proofUrl);
    var receiptRes = await fetch(receiptUrl);
    var headRes = await fetch(headUrl);
    if (proofRes.status === 404 || receiptRes.status === 404) {
      return { word: "MISSING", plain: "No public receipt for this id.", inclusion: false };
    }
    if (!proofRes.ok || !receiptRes.ok || !headRes.ok) {
      return { word: "BROKEN", plain: "Could not fetch public proof JSON.", inclusion: false };
    }
    var proof = await proofRes.json();
    var receipt = await receiptRes.json();
    var head = await headRes.json();
    var leaf = proof.receipt_hash || (proof.inclusion && proof.inclusion.leaf_hash);
    var root = head.root_hash;
    var inclusion = false;
    try {
      inclusion = await verifyInclusion(leaf, root, proof.inclusion || {});
    } catch (err) {
      inclusion = false;
    }
    var word = actWord(receipt, inclusion, Date.now());
    var plain;
    if (word === "BROKEN") {
      plain = "Merkle inclusion failed against the live evidence head.";
    } else if (word === "LATE") {
      plain = "Inclusion holds. Clock is still open past due_at.";
    } else if (word === "AUTHORIZE") {
      plain = "Inclusion holds. Receipt decision is allow.";
    } else if (word === "DECLINE") {
      plain = "Inclusion holds. Receipt decision is a halt.";
    } else {
      plain = "Inclusion holds against evidence-head.json.";
    }
    return {
      word: word,
      plain: plain,
      inclusion: inclusion,
      decision: receipt.decision || null,
      root_hash: root,
      tree_size: head.tree_size,
      due_at: (receipt.canonical_receipt && receipt.canonical_receipt.clock && receipt.canonical_receipt.clock.due_at) || null,
    };
  }

  function bindLookup(root) {
    var input = root.querySelector("[data-receipt-id]");
    var go = root.querySelector("[data-receipt-go]");
    var wordEl = root.querySelector("[data-receipt-word]");
    var plainEl = root.querySelector("[data-receipt-plain]");
    var emptyEl = root.querySelector("[data-receipt-empty]");
    var museumEl = root.querySelector("[data-museum-hop]");
    if (!input || !go || !wordEl) return;

    async function run() {
      var id = (input.value || "").trim();
      if (!id) {
        wordEl.textContent = "—";
        wordEl.className = "proof-word";
        setText(plainEl, "");
        if (emptyEl) emptyEl.hidden = false;
        if (museumEl) museumEl.hidden = true;
        return;
      }
      if (emptyEl) emptyEl.hidden = true;
      wordEl.textContent = "…";
      wordEl.className = "proof-word";
      setText(plainEl, "Folding siblings against the live evidence head…");
      try {
        var result = await lookupReceipt(id);
        wordEl.textContent = result.word;
        wordEl.className = "proof-word " + String(result.word || "").toLowerCase();
        var extra = result.decision ? " Decision on the receipt: " + result.decision + "." : "";
        var hopId = new URLSearchParams(window.location.search).get("hop");
        if (museumEl) museumEl.hidden = hopId !== id;
        if (hopId === id) extra += " Museum hop from /docs — not a production weld.";
        setText(plainEl, (result.plain || "") + extra);
      } catch (err) {
        wordEl.textContent = "BROKEN";
        wordEl.className = "proof-word broken";
        setText(plainEl, "Could not complete the client-side check.");
      }
    }

    go.addEventListener("click", run);
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter") {
        ev.preventDefault();
        run();
      }
    });
    var prefill = new URLSearchParams(window.location.search).get("hop");
    if (prefill) {
      input.value = prefill;
      if (museumEl) museumEl.hidden = false;
      run();
    }
  }

  function bindMerkle(root) {
    var emptyEl = root.querySelector("[data-merkle-empty]");
    var liveEl = root.querySelector("[data-merkle-live]");
    var prevEl = root.querySelector("[data-merkle-prev]");
    var nextEl = root.querySelector("[data-merkle-next]");
    var metaEl = root.querySelector("[data-merkle-meta]");
    var linkEl = root.querySelector("[data-merkle-link]");

    async function load() {
      var res = await fetch("/.well-known/seal-anchor.json");
      if (!res.ok) throw new Error("anchor");
      var body = await res.json();
      var latest = body.latest || {};
      var published = latest.published || null;
      var emptyRoot = body.empty_root || "";
      var leafEl = root.querySelector("[data-empty-leaf]");
      var sibEl = root.querySelector("[data-empty-sib]");
      var foldEl = root.querySelector("[data-empty-fold]");
      var preimageEl = root.querySelector("[data-empty-preimage]");
      if (preimageEl) setText(preimageEl, body.empty_root_preimage || "sha256(ascii gate-evidence-empty)");
      setText(leafEl, shortHash(emptyRoot));
      setText(sibEl, shortHash(emptyRoot));
      if (emptyRoot && foldEl && window.crypto && crypto.subtle) {
        concatHash(hexToBytes(emptyRoot), hexToBytes(emptyRoot))
          .then(function (digest) {
            setText(foldEl, shortHash(bytesToHex(digest)));
          })
          .catch(function () {
            setText(foldEl, "—");
          });
      }
      if (!published || !latest.root_hash) {
        if (emptyEl) emptyEl.hidden = false;
        if (liveEl) liveEl.hidden = true;
        root.classList.remove("is-published");
        return;
      }
      if (emptyEl) emptyEl.hidden = true;
      if (liveEl) liveEl.hidden = false;
      root.classList.add("is-published");
      setText(prevEl, shortHash(latest.prev_root_hash));
      setText(nextEl, shortHash(latest.root_hash));
      var cadence = Number(body.cadence_seconds) || 900;
      var anchored = parseIso(published.anchored_at);
      function tick() {
        var now = Date.now();
        var nextAt = Number.isNaN(anchored) ? NaN : anchored + cadence * 1000;
        var remain = Number.isNaN(nextAt) ? null : nextAt - now;
        var loc = published.locator ? String(published.locator).slice(0, 18) + "…" : "";
        var line = (published.target || "base") + " · " + loc;
        if (remain === null) {
          setText(metaEl, line + " · cadence " + cadence / 60 + " min");
        } else if (remain > 0) {
          setText(metaEl, line + " · next cadence in " + formatRemain(remain));
        } else {
          setText(
            metaEl,
            line + " · last publish aged past " + cadence / 60 + " min — this page does not invent the next tx"
          );
        }
      }
      tick();
      setInterval(tick, 1000);
      if (linkEl && published.locator) {
        var explorers = body.explorers || {};
        var prefix = published.target === "base-sepolia" ? explorers["base-sepolia"] : explorers.base;
        if (prefix) {
          linkEl.href = prefix + published.locator;
          linkEl.hidden = false;
        }
      }
    }

    load().catch(function () {
      if (emptyEl) emptyEl.hidden = false;
      if (liveEl) liveEl.hidden = true;
    });
  }

  function bindClock(root) {
    var emptyEl = root.querySelector("[data-clock-empty]");
    var liveEl = root.querySelector("[data-clock-live]");
    var listEl = root.querySelector("[data-clock-list]");
    var metaEl = root.querySelector("[data-clock-meta]");

    async function load() {
      var res = await fetch("/v1/blotter");
      if (!res.ok) throw new Error("blotter");
      var book = await res.json();
      var rows = book.rows || [];
      var windowMin = book.window_minutes || 60;
      setText(metaEl, windowMin + "-minute window from clock.py. due_at − now(). Not a third-party tape.");
      if (!rows.length) {
        if (emptyEl) emptyEl.hidden = false;
        if (liveEl) liveEl.hidden = true;
        return;
      }
      if (emptyEl) emptyEl.hidden = true;
      if (liveEl) liveEl.hidden = false;
      listEl.innerHTML = "";
      rows.forEach(function (row) {
        var li = document.createElement("li");
        li.className = "settlement-row";
        if (row.composite === "LATE") li.classList.add("is-late");
        li.setAttribute("data-due", row.due_at || "");
        li.setAttribute("data-word", row.composite || "");
        var job = document.createElement("code");
        job.textContent = row.job_id || row.event_id || "";
        var word = document.createElement("span");
        word.className = "proof-word " + String(row.composite || "").toLowerCase();
        word.textContent = row.composite || "—";
        var remain = document.createElement("span");
        remain.className = "settlement-remain";
        remain.setAttribute("data-remain", "1");
        li.appendChild(job);
        li.appendChild(word);
        li.appendChild(remain);
        listEl.appendChild(li);
      });
      function tick() {
        var now = Date.now();
        listEl.querySelectorAll(".settlement-row").forEach(function (li) {
          var due = parseIso(li.getAttribute("data-due"));
          var remain = li.querySelector("[data-remain]");
          if (Number.isNaN(due)) {
            setText(remain, "no due_at");
            return;
          }
          var ms = due - now;
          if (ms <= 0) {
            li.classList.add("is-late");
            setText(remain, "LATE");
          } else {
            setText(remain, formatRemain(ms) + " to LATE");
          }
        });
      }
      tick();
      setInterval(tick, 1000);
    }

    load().catch(function () {
      if (emptyEl) emptyEl.hidden = false;
      if (liveEl) liveEl.hidden = true;
      setText(metaEl, "Could not read the public blotter.");
    });
  }

  document.querySelectorAll("[data-receipt-lookup]").forEach(bindLookup);
  document.querySelectorAll("[data-merkle-strip]").forEach(bindMerkle);
  document.querySelectorAll("[data-settlement-clock]").forEach(bindClock);
})();
