(function (global) {
  function mount(el, opts) {
    opts = opts || {};
    var fuse = opts.fuse_id || el.getAttribute("data-fuse-id") || "";
    var base = opts.base || "";
    el.textContent = "Loading trust status…";
    fetch(base + "/embed/trust.json?fuse_id=" + encodeURIComponent(fuse))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        el.textContent = d.plain || (d.decision ? d.decision : "No public events");
        el.setAttribute("data-decision", d.decision || "NONE");
      })
      .catch(function () {
        el.textContent = "Trust status unavailable";
      });
  }
  global.GateTrustWidget = { mount: mount };
  document.querySelectorAll("[data-gate-trust]").forEach(function (el) {
    mount(el, {});
  });
})(window);
