async function deskJson(url, opts) {
  const res = await fetch(url, Object.assign({ headers: { "Content-Type": "application/json" } }, opts || {}));
  const body = await res.json().catch(() => ({ ok: false, error: "not_json" }));
  body._status = res.status;
  return body;
}

function deskMsg(el, rec) {
  if (!el) return;
  el.className = "desk-msg" + (rec && rec.ok === false ? " err" : "");
  el.textContent = rec.plain || rec.error || JSON.stringify(rec);
}

function layoutGraph(nodes, edges, w, h) {
  const cx = w / 2, cy = h / 2, r = Math.min(w, h) * 0.36;
  const placed = nodes.map((n, i) => {
    const a = (Math.PI * 2 * i) / Math.max(nodes.length, 1) - Math.PI / 2;
    return Object.assign({}, n, { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) });
  });
  const byId = Object.fromEntries(placed.map((n) => [n.node_id, n]));
  return { nodes: placed, edges: edges.filter((e) => byId[e.from_node_id] && byId[e.to_node_id]), byId };
}

function drawGraph(svg, graph, onClick) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  const w = 720, h = 420;
  svg.setAttribute("viewBox", "0 0 " + w + " " + h);
  const laid = layoutGraph(graph.nodes || [], graph.edges || [], w, h);
  laid.edges.forEach((e) => {
    const a = laid.byId[e.from_node_id], b = laid.byId[e.to_node_id];
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
    line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
    line.setAttribute("class", "e e-" + e.edge_type);
    svg.appendChild(line);
  });
  laid.nodes.forEach((n) => {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", n.x); c.setAttribute("cy", n.y); c.setAttribute("r", 6);
    c.setAttribute("class", "n n-" + n.entity_type);
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", n.x + 8); t.setAttribute("y", n.y + 3);
    t.textContent = (n.entity_ref || "").slice(0, 18);
    g.appendChild(c); g.appendChild(t);
    g.style.cursor = "pointer";
    g.addEventListener("click", () => onClick(n));
    svg.appendChild(g);
  });
}

document.addEventListener("submit", async (ev) => {
  const form = ev.target;
  if (!(form instanceof HTMLFormElement) || !form.dataset.desk) return;
  ev.preventDefault();
  const url = form.getAttribute("action");
  const method = (form.getAttribute("method") || "POST").toUpperCase();
  const payload = {};
  new FormData(form).forEach((v, k) => {
    if (k.endsWith("[]")) {
      const key = k.slice(0, -2);
      payload[key] = payload[key] || [];
      payload[key].push(v);
    } else if (v === "true" || v === "false") {
      payload[k] = v === "true";
    } else if (v !== "") {
      payload[k] = v;
    }
  });
  ["linked_receipt_ids", "linked_anomaly_flag_ids", "member_operator_ids", "evidence_receipt_ids", "confounder_considered", "receipt_hashes"].forEach((k) => {
    if (typeof payload[k] === "string") {
      payload[k] = payload[k].split(/[\s,]+/).map((s) => s.trim()).filter(Boolean);
    }
  });
  const rec = await deskJson(url, { method, body: method === "GET" ? undefined : JSON.stringify(payload) });
  deskMsg(form.querySelector(".desk-msg"), rec);
  if (rec.ok && form.dataset.reload === "1") window.location.reload();
});
