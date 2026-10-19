const $ = (s) => document.querySelector(s);

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".reveal").forEach((el) => {
    requestAnimationFrame(() => el.classList.add("in"));
  });

  const form = $("#leadForm");
  if (form) {
    form.addEventListener("submit", (e) => {
      const btn = form.querySelector(".btn");
      btn.disabled = true;
      btn.querySelector("span") ? (btn.querySelector("span").textContent = "Processing...") : (btn.textContent = "Processing...");
    });
  }
});

function animateNum(el, target) {
  const start = parseInt(el.textContent) || 0;
  if (start === target) return;
  const t0 = performance.now(), dur = 900;
  function step(t) {
    const p = Math.min((t - t0) / dur, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(start + (target - start) * eased);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

async function initDashboard() {
  await refresh();
  setInterval(refresh, 6000);
}

async function refresh() {
  try {
    const [statsR, leadsR, logsR] = await Promise.all([
      fetch("/api/stats"), fetch("/api/submissions"), fetch("/api/logs"),
    ]);
    const stats = await statsR.json();
    const leads = await leadsR.json();
    const logs = await logsR.json();
    renderStats(stats);
    renderLeads(leads);
    renderLogs(logs);
    renderBars(stats.services, stats.total);
  } catch (e) {
    console.error("refresh failed", e);
  }
}

function renderStats(s) {
  animateNum($("#s-total"), s.total);
  animateNum($("#s-today"), s.today);
  animateNum($("#s-emails"), s.emails_sent + s.demo_emails);
  animateNum($("#s-logs"), s.logs);
}

function renderLeads(rows) {
  const tb = $("#leadTable tbody");
  if (!rows.length) { tb.innerHTML = `<tr><td colspan="6" class="empty">Abhi koi lead nahi - pehla form submit karein</td></tr>`; return; }
  tb.innerHTML = rows.slice(0, 12).map((r) => `
    <tr>
      <td>#${esc(r.id)}</td>
      <td><b>${esc(r.name)}</b></td>
      <td>${esc(r.service || "-")}</td>
      <td>${esc(r.email)}</td>
      <td><span class="tag ${esc(r.email_status)}">${esc(r.email_status)}</span></td>
      <td>${esc(r.timestamp)}</td>
    </tr>`).join("");
}

function renderLogs(rows) {
  const ul = $("#logList");
  if (!rows.length) { ul.innerHTML = `<li class="empty">No automation runs yet</li>`; return; }
  ul.innerHTML = rows.slice(0, 20).map((l) => `
    <li class="${esc(l.status)}">
      <b>${esc(l.action)}</b> - ${esc(l.status)}
      <span class="t">${esc(l.detail)} &middot; ${esc(l.timestamp)}</span>
    </li>`).join("");
}

function renderBars(services, total) {
  const box = $("#bars");
  const entries = Object.entries(services).sort((a, b) => b[1] - a[1]);
  if (!entries.length) { box.innerHTML = `<div class="empty">No data</div>`; return; }
  box.innerHTML = entries.map(([k, v]) => {
    const pct = total ? Math.round((v / total) * 100) : 0;
    return `<div class="bar-row">
      <div class="lbl"><span>${esc(k)}</span><span>${v} (${pct}%)</span></div>
      <div class="bar"><i data-w="${pct}"></i></div>
    </div>`;
  }).join("");
  requestAnimationFrame(() => box.querySelectorAll(".bar i").forEach((i) => (i.style.width = i.dataset.w + "%")));
}
