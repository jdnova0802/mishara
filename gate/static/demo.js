(function () {
  const out = document.getElementById("demo-output");
  const btn = document.getElementById("demo-hop-btn");
  const verifyLink = document.getElementById("demo-verify-link");
  if (!btn || !out) return;

  btn.addEventListener("click", async function () {
    btn.disabled = true;
    btn.textContent = "Hopping…";
    out.textContent = "Calling live fuse hop…";
    verifyLink.style.display = "none";

    try {
      const r = await fetch("/demo/hop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fuse_id: "fuse_velaru_drill" }),
      });
      const data = await r.json();
      out.textContent = JSON.stringify(data, null, 2);

      if (data.verify_url) {
        verifyLink.href = data.verify_url;
        verifyLink.textContent = "Open verify proof →";
        verifyLink.style.display = "inline-block";
      }
    } catch (e) {
      out.textContent = "Error: " + e.message;
    } finally {
      btn.disabled = false;
      btn.textContent = "Run live hop";
    }
  });
})();
