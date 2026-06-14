const API = "";

const QUICK_PROMPTS = [
  {
    label: "Utwórz WWW chat",
    prompt: "stwórz prosty web UI hypervisora jako chat markdown połączony z API systemu",
  },
  {
    label: "Dashboard agent",
    prompt: "stwórz dashboard agenta hypervisor-dashboard do pokazywania procesów i napraw",
  },
  {
    label: "Status agenta",
    prompt: "pokaż proces agenta weather-map-agent.local",
  },
  {
    label: "User agent",
    prompt: "pokaż health agenta user-agent.local",
  },
  {
    label: "Invoices agent",
    prompt: "zdiagnozuj agenta invoices-agent.local",
  },
  {
    label: "Diagnoza",
    prompt: "zdiagnozuj agenta weather-map-agent.local i pokaż plan naprawy",
  },
];

const conversationLog = [];

const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const promptEl = document.getElementById("prompt");
const dryRunEl = document.getElementById("dry-run");
const sendBtn = document.getElementById("send-btn");
const statusPill = document.getElementById("status-pill");
const apiDetail = document.getElementById("api-detail");
const refreshBtn = document.getElementById("refresh-btn");
const copyChatBtn = document.getElementById("copy-chat-btn");
const quickPromptsEl = document.getElementById("quick-prompts");
const agentListEl = document.getElementById("agent-list");
const eventListEl = document.getElementById("event-list");

if (window.marked) {
  marked.setOptions({ breaks: true, gfm: true });
}

function renderMarkdown(text) {
  if (window.marked && window.DOMPurify) {
    const raw = marked.parse(text || "");
    return DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } });
  }
  return renderBasicMarkdown(text || "");
}

function renderBasicMarkdown(text) {
  const blocks = [];
  const pattern = /```(\w+)?\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      blocks.push(renderBasicText(text.slice(lastIndex, match.index)));
    }
    blocks.push(`<pre><code>${escapeHtml(match[2].trim())}</code></pre>`);
    lastIndex = pattern.lastIndex;
  }
  if (lastIndex < text.length) {
    blocks.push(renderBasicText(text.slice(lastIndex)));
  }
  return blocks.join("");
}

function renderBasicText(text) {
  return text
    .split(/\n{2,}/)
    .map((paragraph) => {
      const lines = paragraph.trim().split("\n");
      if (!paragraph.trim()) return "";
      if (lines[0].startsWith("## ")) {
        return `<h2>${inlineMarkdown(lines[0].slice(3))}</h2>`;
      }
      if (lines.every((line) => line.startsWith("- "))) {
        return `<ul>${lines.map((line) => `<li>${inlineMarkdown(line.slice(2))}</li>`).join("")}</ul>`;
      }
      return `<p>${inlineMarkdown(lines.join("\n")).replace(/\n/g, "<br>")}</p>`;
    })
    .join("");
}

function inlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function extractUri(text) {
  const match = text.match(/([a-z][a-z0-9+.-]*:\/\/[^\s`'")]+)/i);
  return match ? match[1].replace(/[.,;]+$/, "") : null;
}

function extractUrisFromText(text) {
  const matches = text.match(/[a-z][a-z0-9+.-]*:\/\/[^\s`'")]+/gi) || [];
  return [...new Set(matches.map((item) => item.replace(/[.,;]+$/, "")))];
}

function collectUris(data) {
  if (!data || typeof data !== "object") return [];
  const uris = [];
  for (const key of ["planned_uris", "uris"]) {
    if (Array.isArray(data[key])) uris.push(...data[key]);
  }
  if (typeof data.uri === "string") uris.push(data.uri);
  if (Array.isArray(data.actions)) {
    data.actions.forEach((action) => {
      if (action && typeof action.uri === "string") uris.push(action.uri);
    });
  }
  return [...new Set(uris.filter((uri) => typeof uri === "string" && uri.includes("://")))];
}

function looksLikeUri(text) {
  return /[a-z][a-z0-9+.-]*:\/\//i.test(text.trim());
}

function htmlToPlainText(html) {
  const div = document.createElement("div");
  div.innerHTML = html;
  return (div.innerText || div.textContent || "").trim();
}

function buildConversationMarkdown() {
  const lines = ["# Taskinity Chat", ""];
  conversationLog.forEach((entry) => {
    lines.push(`## ${entry.role === "user" ? "Ty" : "System"}`);
    lines.push("");
    lines.push(entry.text);
    lines.push("");
  });
  return lines.join("\n").trim();
}

async function copyToClipboard(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.left = "-9999px";
  document.body.appendChild(area);
  area.select();
  document.execCommand("copy");
  document.body.removeChild(area);
}

function flashButtonFeedback(button, okLabel = "Skopiowano") {
  if (!button) return;
  const original = button.textContent;
  button.textContent = okLabel;
  button.disabled = true;
  window.setTimeout(() => {
    button.textContent = original;
    button.disabled = false;
  }, 1400);
}

async function copyConversation() {
  const markdown = buildConversationMarkdown();
  if (!markdown || conversationLog.length === 0) {
    flashButtonFeedback(copyChatBtn, "Brak treści");
    return;
  }
  try {
    await copyToClipboard(markdown);
    flashButtonFeedback(copyChatBtn);
  } catch (err) {
    flashButtonFeedback(copyChatBtn, "Błąd kopiowania");
    console.error(err);
  }
}

function appendMessage(role, bodyHtml, { text, error = false, uris = [] } = {}) {
  const bodyText = text ?? htmlToPlainText(bodyHtml);
  conversationLog.push({ role, text: bodyText });
  const wrap = document.createElement("article");
  wrap.className = `msg msg--${role}${error ? " msg--error" : ""}`;
  wrap.innerHTML = `
    <div class="msg-role">${role === "user" ? "Ty" : "System"}</div>
    <div class="msg-body">${bodyHtml}</div>
  `;
  messagesEl.appendChild(wrap);
  enhanceBlocks(wrap);
  appendUriActions(wrap, uris);
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
    copyBtn.addEventListener("click", async () => {
      try {
        await copyToClipboard(text.trim());
        flashButtonFeedback(copyBtn);
      } catch (err) {
        console.error(err);
      }
    });
    actions.appendChild(copyBtn);

    if (uri) {
      actions.appendChild(actionButton("Podgląd URI", () => previewUri(uri)));
      actions.appendChild(actionButton(dryRunEl.checked ? "Dry-run URI" : "Wykonaj URI", () => callUri(uri)));
    }

    codeEl.parentElement?.insertAdjacentElement("afterend", actions);
  });
}

function appendUriActions(root, uris) {
  const uniqueUris = [...new Set([...(uris || []), ...extractUrisFromText(root.textContent || "")])];
  if (!uniqueUris.length) return;

  const actions = document.createElement("div");
  actions.className = "uri-actions";
  uniqueUris.slice(0, 6).forEach((uri) => {
    actions.appendChild(actionButton(shortUri(uri), () => previewUri(uri), "uri-chip"));
  });
  root.appendChild(actions);
}

function actionButton(label, handler, className = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", handler);
  return button;
}

function shortUri(uri) {
  return uri.length > 46 ? `${uri.slice(0, 43)}...` : uri;
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

async function checkHealth({ silent = false } = {}) {
  try {
    const health = await apiFetch("/health");
    statusPill.textContent = `${health.agent} · OK`;
    statusPill.className = "pill pill--ok";
    apiDetail.textContent = `${health.version || "dev"} · ${API || "same-origin"}`;
    return health;
  } catch (err) {
    statusPill.textContent = "brak API";
    statusPill.className = "pill pill--warn";
    apiDetail.textContent = "offline";
    if (!silent) {
      appendMessage(
        "assistant",
        `<p>Brak połączenia z API. Uruchom serwer:</p><pre><code>urish www serve</code></pre><p>${escapeHtml(String(err))}</p>`,
        { error: true },
      );
    }
    return null;
  }
}

async function loadSystemState() {
  await checkHealth({ silent: true });
  await Promise.all([loadAgents(), loadEvents()]);
}

async function loadAgents() {
  try {
    const payload = await apiFetch("/api/agents");
    const agents = payload.agents || [];
    if (!agents.length) {
      agentListEl.className = "list list--empty";
      agentListEl.textContent = "brak wpisów";
      return;
    }
    agentListEl.className = "list";
    agentListEl.innerHTML = "";
    agents.slice(0, 6).forEach((agent) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "list-item";
      item.innerHTML = `<strong>${escapeHtml(agent.id)}</strong><span>${escapeHtml(agent.status || "unknown")}</span>`;
      item.addEventListener("click", () => callUri(agent.view_uri || `view://process/agent/${agent.id}/latest`));
      agentListEl.appendChild(item);
    });
  } catch (err) {
    agentListEl.className = "list list--empty";
    agentListEl.textContent = "API niedostępne";
  }
}

async function loadEvents() {
  try {
    const payload = await apiFetch("/api/events?limit=5");
    const events = payload.events || [];
    if (!events.length) {
      eventListEl.className = "list list--empty";
      eventListEl.textContent = "brak zdarzeń";
      return;
    }
    eventListEl.className = "list";
    eventListEl.innerHTML = "";
    events.forEach((event) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "list-item";
      item.innerHTML = `<strong>${escapeHtml(event.type)}</strong><span>${escapeHtml(event.agent_id || event.uri || "")}</span>`;
      if (event.uri) item.addEventListener("click", () => callUri(event.uri));
      eventListEl.appendChild(item);
    });
  } catch (err) {
    eventListEl.className = "list list--empty";
    eventListEl.textContent = "API niedostępne";
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
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

async function previewUri(uri) {
  appendMessage("user", `<p>Podgląd <code>${escapeHtml(uri)}</code></p>`, {
    text: `Podgląd \`${uri}\``,
  });
  setBusy(true);
  try {
    const result = await apiFetch("/api/uri/preview", {
      method: "POST",
      body: JSON.stringify({
        uri,
        dry_run: true,
        policy: "dev",
      }),
    });
    appendMessage("assistant", renderMarkdown(formatPreviewMarkdown(result)), {
      uris: [uri],
      text: formatPreviewMarkdown(result),
    });
  } catch (err) {
    appendMessage("assistant", `<p><strong>Błąd preview</strong></p><p>${escapeHtml(String(err))}</p>`, {
      error: true,
    });
  } finally {
    setBusy(false);
  }
}

function formatPreviewMarkdown(result) {
  const approval = result.requires_approval ? "tak" : "nie";
  const dryRun = result.dry_run_allowed ? "tak" : "nie";
  const execute = result.execute_allowed_with_approval ? "tak" : "nie";
  return [
    "## Podgląd URI",
    `URI: \`${result.uri}\``,
    `Dry-run: **${dryRun}** · wymaga approval: **${approval}** · execute po approval: **${execute}**`,
    "",
    "```json",
    JSON.stringify(result, null, 2),
    "```",
  ].join("\n");
}

async function callUri(uri, { approved = false, echoUser = true } = {}) {
  if (echoUser) {
    appendMessage("user", `<p><code>${escapeHtml(uri)}</code></p>`, { text: `\`${uri}\`` });
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
    appendMessage("assistant", renderMarkdown(md), { uris: collectUris(result.data), text: md });
    await loadSystemState();
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
  refreshBtn.disabled = busy;
  if (copyChatBtn) copyChatBtn.disabled = busy;
}

async function handleSubmit(event) {
  event.preventDefault();
  const text = promptEl.value.trim();
  if (!text) return;

  appendMessage("user", `<p>${escapeHtml(text)}</p>`, { text });
  promptEl.value = "";
  setBusy(true);

  try {
    if (looksLikeUri(text)) {
      const uri = extractUri(text) || text.trim();
      await callUri(uri, { echoUser: false });
      return;
    }

    const result = await askPrompt(text);
    const md = result.message_markdown || "_Brak odpowiedzi._";
    appendMessage("assistant", renderMarkdown(md), {
      uris: collectUris(result.data),
      text: md,
    });
  } catch (err) {
    appendMessage("assistant", `<p><strong>Błąd ask</strong></p><p>${escapeHtml(String(err))}</p>`, {
      error: true,
    });
  } finally {
    setBusy(false);
  }
}

function renderQuickPrompts() {
  quickPromptsEl.innerHTML = "";
  QUICK_PROMPTS.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = item.label;
    button.dataset.prompt = item.prompt;
    button.addEventListener("click", () => {
      promptEl.value = item.prompt;
      promptEl.focus();
    });
    quickPromptsEl.appendChild(button);
  });
}

form.addEventListener("submit", handleSubmit);
refreshBtn.addEventListener("click", () => loadSystemState());
copyChatBtn?.addEventListener("click", () => copyConversation());
promptEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

renderQuickPrompts();
appendMessage(
  "assistant",
  renderMarkdown(
    "## Hypervisor Chat\n\n" +
      "Połączony widok NL → URI → wynik. Zacznij od komendy z panelu albo wpisz własne polecenie.\n\n" +
      "```bash\n" +
      "urish www create \"stwórz prosty chat markdown połączony z API systemu\" --plan-only\n" +
      "urish www serve\n" +
      "```",
  ),
  {
    text:
      "## Hypervisor Chat\n\n" +
      "Połączony widok NL → URI → wynik. Zacznij od komendy z panelu albo wpisz własne polecenie.\n\n" +
      "```bash\n" +
      "urish www create \"stwórz prosty chat markdown połączony z API systemu\" --plan-only\n" +
      "urish www serve\n" +
      "```",
  },
);

loadSystemState();
