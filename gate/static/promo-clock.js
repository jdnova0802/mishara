/**
 * Promo Clock — fail-closed marketing dates for liveness surfaces.
 * Past "Next drill" must not render as upcoming.
 *
 * Usage:
 *   <div class="drill-bar" data-promo-clock
 *        data-next-at="2026-08-18T17:00:00-07:00"
 *        data-last-proved-at="2026-08-24T06:31:00Z"
 *        data-label="AWS Loft SF"
 *        data-href="/fuse/fuse_velaru_drill"></div>
 *   <script src="https://gate.velaru.xyz/static/promo-clock.js" defer></script>
 *
 * Or set window.PROMO_CLOCK = { next_at, last_proved_at, label, href }
 * before load; targets #drill-bar by default.
 */
(function () {
  "use strict";

  function parseTs(s) {
    if (!s || !String(s).trim()) return null;
    var t = String(s).trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(t)) t += "T23:59:59Z";
    var d = new Date(t);
    return isNaN(d.getTime()) ? null : d;
  }

  function fmt(d) {
    try {
      return d.toLocaleString(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        timeZoneName: "short",
      });
    } catch (e) {
      return d.toISOString();
    }
  }

  function evaluate(cfg, now) {
    now = now || new Date();
    var next = parseTs(cfg.next_at);
    var proved = parseTs(cfg.last_proved_at);
    if (cfg.next_at && !next) {
      return { mode: "invalid", render: false };
    }
    if (next && next.getTime() > now.getTime()) {
      return {
        mode: "upcoming",
        render: true,
        headline: "Next drill",
        when: next,
        label: cfg.label,
        href: cfg.href,
      };
    }
    if (proved) {
      return {
        mode: "proved",
        render: true,
        headline: "Last proved",
        when: proved,
        label: cfg.label,
        href: cfg.href,
        stale: !!(next && next.getTime() <= now.getTime()),
      };
    }
    return {
      mode: "hidden",
      render: false,
      stale: !!(next && next.getTime() <= now.getTime()),
    };
  }

  function apply(el, state) {
    if (!el) return;
    if (!state.render) {
      el.hidden = true;
      el.setAttribute("data-promo-mode", state.mode || "hidden");
      el.innerHTML = "";
      return;
    }
    el.hidden = false;
    el.setAttribute("data-promo-mode", state.mode);
    var parts = ["<strong>" + state.headline + "</strong>"];
    if (state.label) parts.push(escapeHtml(state.label));
    if (state.when) parts.push(escapeHtml(fmt(state.when)));
    var html = parts.join(" · ");
    if (state.href) {
      html += ' · <a href="' + escapeAttr(state.href) + '">open →</a>';
    }
    el.innerHTML = html;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  function cfgFromEl(el) {
    return {
      next_at: el.getAttribute("data-next-at") || el.getAttribute("data-promo-next"),
      last_proved_at:
        el.getAttribute("data-last-proved-at") ||
        el.getAttribute("data-promo-proved"),
      label: el.getAttribute("data-label") || el.getAttribute("data-promo-label"),
      href: el.getAttribute("data-href") || el.getAttribute("data-promo-href"),
    };
  }

  function run() {
    var nodes = document.querySelectorAll("[data-promo-clock]");
    if (!nodes.length) {
      var bar = document.getElementById("drill-bar");
      if (bar) {
        var globalCfg = window.PROMO_CLOCK || {};
        // Prefer data-* on the bar if present; else global; else parse legacy text (last resort: hide if Aug past)
        var cfg = Object.assign({}, globalCfg, cfgFromEl(bar));
        if (!cfg.next_at && !cfg.last_proved_at) {
          // Legacy hardcoded Check banner: fail closed if it still says a past calendar date
          var text = (bar.textContent || "").toLowerCase();
          var m = text.match(
            /(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\s+\d{4}/i
          );
          if (m) {
            try {
              var guessed = new Date(m[0] + " 23:59:59 UTC");
              if (!isNaN(guessed.getTime()) && guessed.getTime() < Date.now()) {
                // Prefer last restraint feed item if page exposed RECENT_BLOCKS
                if (
                  window.RECENT_BLOCKS &&
                  window.RECENT_BLOCKS[0] &&
                  window.RECENT_BLOCKS[0].issued_at
                ) {
                  cfg.last_proved_at = window.RECENT_BLOCKS[0].issued_at;
                  cfg.label = cfg.label || "public restraint";
                  cfg.href =
                    cfg.href ||
                    (window.RECENT_BLOCKS[0].fuse_id
                      ? "/fuse/" + window.RECENT_BLOCKS[0].fuse_id
                      : null);
                } else {
                  apply(bar, { mode: "hidden", render: false, stale: true });
                  return;
                }
              }
            } catch (e) {
              apply(bar, { mode: "hidden", render: false });
              return;
            }
          }
        }
        apply(bar, evaluate(cfg));
      }
      return;
    }
    nodes.forEach(function (el) {
      apply(el, evaluate(cfgFromEl(el)));
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  window.PromoClock = { evaluate: evaluate, run: run };
})();
