// QueueStorm Warmup — frontend logic.
// Talks to the same FastAPI service that powers the /sort-ticket endpoint.

const API_BASE = ""; // same origin

const SAMPLE_CASES = [
  {
    id: 1,
    message: "I sent 3000 to wrong number this morning, please help me get it back",
    expected: "wrong_transfer / high",
  },
  {
    id: 2,
    message: "Payment failed but my balance was deducted 200 taka, please check",
    expected: "payment_failed / high",
  },
  {
    id: 3,
    message: "Someone called asking for my OTP, is that bKash? Should I share?",
    expected: "phishing / critical",
  },
  {
    id: 4,
    message: "Please refund my last transaction, I changed my mind",
    expected: "refund_request / low",
  },
  {
    id: 5,
    message: "App crashed when I opened it this morning, cannot login",
    expected: "other / low",
  },
];

// ---------- Health probe ----------
async function refreshHealth() {
  const pill = document.getElementById("healthPill");
  const label = document.getElementById("healthLabel");
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    pill.classList.add("ok");
    pill.classList.remove("fail");
    label.textContent = `ok — v${data.version ?? "?"}`;
  } catch (err) {
    pill.classList.add("fail");
    pill.classList.remove("ok");
    label.textContent = "unreachable";
  }
}

// ---------- Single ticket ----------
async function classifyOne(ticketId, message) {
  const out = document.getElementById("output");
  const review = document.getElementById("reviewBanner");
  out.textContent = "Classifying...";
  review.classList.remove("show");
  clearMeta();

  try {
    const res = await fetch(`${API_BASE}/sort-ticket`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticket_id: ticketId,
        channel: "app",
        locale: "en",
        message: message,
      }),
    });
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); } catch { throw new Error(text); }
    if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);

    renderResult(data);
  } catch (err) {
    out.textContent = "Error";
    out.innerHTML = `<div class="error">${escapeHtml(String(err))}</div>`;
  }
}

function renderResult(data) {
  const out = document.getElementById("output");
  out.textContent = JSON.stringify(data, null, 2);

  // Severity / case chips
  setMeta("case_type", data.case_type);
  setMeta("severity", data.severity, data.severity);
  setMeta("department", data.department);
  setMeta("confidence", data.confidence?.toFixed?.(2) ?? data.confidence);
  setMeta("human_review", String(data.human_review_required), data.human_review_required ? "review" : null);

  const banner = document.getElementById("reviewBanner");
  if (data.human_review_required) {
    banner.textContent =
      data.case_type === "phishing_or_social_engineering"
        ? "⚠️ Phishing / social-engineering suspected. Human review required immediately."
        : "⚠️ Critical severity. Human review required.";
    banner.classList.add("show");
  } else {
    banner.classList.remove("show");
  }
}

function clearMeta() {
  ["case_type", "severity", "department", "confidence", "human_review"].forEach((k) => {
    const el = document.getElementById(`meta-${k}`);
    if (el) {
      el.querySelector(".v").textContent = "—";
      el.classList.remove("critical", "high", "medium", "low", "review");
    }
  });
}

function setMeta(key, value, severityClass) {
  const el = document.getElementById(`meta-${key}`);
  if (!el) return;
  el.querySelector(".v").textContent = value ?? "—";
  el.classList.remove("critical", "high", "medium", "low", "review");
  if (severityClass) el.classList.add(severityClass);
}

// ---------- Sample runner ----------
function renderSamples() {
  const wrap = document.getElementById("samples");
  wrap.innerHTML = "";
  SAMPLE_CASES.forEach((s, i) => {
    const div = document.createElement("div");
    div.className = "sample";
    div.innerHTML = `
      <span class="tag">CASE ${i + 1} · expected: ${escapeHtml(s.expected)}</span>
      <div class="msg">${escapeHtml(s.message)}</div>
    `;
    div.addEventListener("click", () => {
      document.getElementById("ticketId").value = `T-${String(i + 1).padStart(3, "0")}`;
      document.getElementById("message").value = s.message;
      classifyOne(`T-${String(i + 1).padStart(3, "0")}`, s.message);
    });
    wrap.appendChild(div);
  });
}

async function runAllSamples() {
  const resultsEl = document.getElementById("samplesOutput");
  resultsEl.innerHTML = `<div class="spinner">Running all 5 cases against /sort-ticket...</div>`;
  const summary = [];
  for (let i = 0; i < SAMPLE_CASES.length; i++) {
    const s = SAMPLE_CASES;
    const ticketId = `T-${String(i + 1).padStart(3, "0")}`;
    try {
      const res = await fetch(`${API_BASE}/sort-ticket`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticket_id: ticketId,
          channel: "app",
          locale: "en",
          message: s[i].message,
        }),
      });
      const data = await res.json();
      summary.push({ n: i + 1, expected: s[i].expected, got: data });
    } catch (err) {
      summary.push({ n: i + 1, expected: s[i].expected, error: String(err) });
    }
  }
  resultsEl.textContent = JSON.stringify(summary, null, 2);
}

// ---------- helpers ----------
function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

// ---------- wire up ----------
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("classifyBtn").addEventListener("click", () => {
    const ticketId = document.getElementById("ticketId").value.trim() || "T-001";
    const message = document.getElementById("message").value.trim();
    if (!message) {
      document.getElementById("output").innerHTML =
        `<div class="error">Please type a customer message first.</div>`;
      return;
    }
    classifyOne(ticketId, message);
  });

  document.getElementById("runAllBtn").addEventListener("click", runAllSamples);

  document.getElementById("clearBtn").addEventListener("click", () => {
    document.getElementById("ticketId").value = "T-001";
    document.getElementById("message").value = "";
    document.getElementById("output").textContent = "// response will appear here";
    clearMeta();
    document.getElementById("reviewBanner").classList.remove("show");
  });

  renderSamples();
  refreshHealth();
  setInterval(refreshHealth, 15000);
});
