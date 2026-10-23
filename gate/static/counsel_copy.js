(function () {
  "use strict";

  function textFromCounsel(counsel) {
    if (counsel && counsel.text) return counsel.text;
    return "";
  }

  function bindCard(root) {
    var go = root.querySelector("[data-counsel-go]");
    var status = root.querySelector("[data-counsel-status]");
    var preview = root.querySelector("[data-counsel-preview]");
    if (!go) return;

    async function copy(text) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (err) {
        if (preview) {
          preview.hidden = false;
          preview.value = text;
          preview.focus();
          preview.select();
        }
        return false;
      }
    }

    go.addEventListener("click", async function () {
      go.disabled = true;
      if (status) status.textContent = "Minting a museum hop…";
      try {
        var r = await fetch("/demo/hop", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fuse_id: "fuse_velaru_drill" }),
        });
        var data = await r.json();
        var counsel = data.counsel || {};
        var text = textFromCounsel(counsel);
        if (!text) {
          if (status) status.textContent = "Hop returned no counsel object.";
          return;
        }
        if (preview) {
          preview.hidden = false;
          preview.value = text;
        }
        var ok = await copy(text);
        if (status) {
          status.textContent = ok
            ? "Copied. Museum hop — not a production weld."
            : "Select the text and copy. Museum hop — not a production weld.";
        }
        var check = root.querySelector("[data-counsel-check]");
        if (check && counsel.check_url) {
          check.href = counsel.check_url;
          check.hidden = false;
        }
      } catch (err) {
        if (status) status.textContent = "Could not mint a museum hop.";
      } finally {
        go.disabled = false;
      }
    });
  }

  document.querySelectorAll("[data-counsel-card]").forEach(bindCard);
})();
