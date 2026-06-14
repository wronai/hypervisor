const API = "";

const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const promptEl = document.getElementById("prompt");
const dryRunEl = document.getElementById("dry-run");
const sendBtn = document.getElementById("send-btn");
const statusPill = document.getElementById("status-pill");

marked.setOptions({ breaks: true, gfm: true });

function renderMarkdown(text) {
  const raw = marked.parse(text || "");
  return DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } });
}

function extractUri(text) {
  const match = text.match(/([a-z][a-z0-9+.-]*:\/\/[^\s`'"]+)/i);
  return match ? match[1].replace(/[.,;]+$/, "") : null;
}

function looksLikeUri(text) {
  return /[a-z][a-z0-9+.-]*:\/\//i.test(text.trim());
}

function appendMessage(role, bodyHtml, { error = false } = {}) {
  const wrap = document.createElement("article");
  wrap.className = `msg msg--${role}${error ? " msg--error" : ""}`;
  wrap.innerHTML = `
    <div class="msg-role">${role === "user" ? "Ty" : "System"}</div>
    <div class="msg-body">${bodyHtml}</div>
  `;
  messagesEl.appendChild(wrap);
  enhanceBlocks(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return wrap;
}

function enhanceBlocks(root) {
  root.querySelectorAll("pre > code").forEach((codeEl) => {
    const text = codeEl.textContent || "";
    const uri = extractUri(text);
    const actions = document.createElement("div");
    actions.className = "block-actions";

    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.textContent = "Kopiuj";
    copyBtn.addEventListener("click", () => navigator.clipboard.writeText(text.trim()));
    actions.appendChild(copyBtn);

    if (uri) {
      const runBtn = document.createElement("button");
      runBtn.type = "button";
      runBtn.textContent = dryRunEl.checked ? "Dry-run URI" : "Wykonaj URI";
      runBtn.addEventListener("click", () => callUri(uri));
      actions.appendChild(runBtn);
    }

    codeEl.parentElement?.insertAdjacentElement("afterend", actions);
  });
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = payload.detail || payload.error || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

async function checkHealth() {
  try {
    const health = await apiFetch("/health");
    statusPill.textContent = `${health.agent} · OK`;
    statusPill.className = "pill pill--ok";
  } catch (err) {
    statusPill.textContent = "brak API";
    statusPill.className = "pill pill--warn";
    appendMessage(
      "assistant",
      `<p>Brak połączenia z API. Uruchom serwer:</p><pre><code>urish www serve</code></pre><p>${escapeHtml(String(err))}</p>`,
      { error: true },
    );
  }
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function askPrompt(text) {
  return apiFetch("/api/ask", {
    method: "POST",
    body: JSON.stringify({
      prompt: text,
      dry_run: dryRunEl.checked,
      llm: false,
    }),
  });
}

async function callUri(uri, { approved = false, echoUser = true } = {}) {
  if (echoUser) {
    appendMessage("user", `<p><code>${escapeHtml(uri)}</code></p>`);
  }
  setBusy(true);
  try {
    const result = await apiFetch("/api/uri/call", {
      method: "POST",
      body: JSON.stringify({
        uri,
        dry_run: dryRunEl.checked && !approved,
        approved,
        policy: "dev",
      }),
    });
    const md = result.message_markdown || "```json\n" + JSON.stringify(result, null, 2) + "\n```";
    appendMessage("assistant", renderMarkdown(md));
  } catch (err) {
    appendMessage("assistant", `<p><strong>Błąd URI</strong></p><p>${escapeHtml(String(err))}</p>`, {
      error: true,
    });
  } finally {
    setBusy(false);
  }
}

function setBusy(busy) {
  sendBtn.disabled = busy;
  promptEl.disabled = busy;
}

async function handleSubmit(event) {
  event.preventDefault();
  const text = promptEl.value.trim();
  if (!text) return;

  appendMessage("user", `<p>${escapeHtml(text)}</p>`);
  promptEl.value = "";
  setBusy(true);

  try {
    if (looksLikeUri(text)) {
      const uri = extractUri(text) || text.trim();
      await callUri(uri, { echoUser: false });
      return;
    }

    const result = await askPrompt(text);
    appendMessage("assistant", renderMarkdown(result.message_markdown || "_Brak odpowiedzi._"));
  } catch (err) {
    appendMessage("assistant", `<p><strong>Błąd ask</strong></p><p>${escapeHtml(String(err))}</p>`, {
      error: true,
    });
  } finally {
    setBusy(false);
  }
}

form.addEventListener("submit", handleSubmit);
promptEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

appendMessage(
  "assistant",
  renderMarkdown(
    "## Witaj w Hypervisor Chat\n\n" +
      "Wpisz prompt po polsku lub angielsku — np.:\n\n" +
      "- `stwórz dashboard agenta hypervisor`\n" +
      "- `ecosystem weather demo`\n\n" +
      "Albo wklej URI (`agent://…`, `view://…`) aby wykonać przez policy gate.\n\n" +
      "Odpowiedzi renderują się jako **markdown** z planowanymi URI i komendami `urish`.",
  ),
);

checkHealth();
