function renderUriResult(data) {
  const result = document.getElementById("result");
  if (!result) return;
  if (data.message_markdown) {
    result.textContent = data.message_markdown;
  } else {
    result.textContent = JSON.stringify(data, null, 2);
  }
}

function shouldRefreshPage(data, { approved = false } = {}) {
  if (!approved || data.ok === false) {
    return false;
  }
  const resultType = String(data.result_type || "");
  return resultType === "repair" || resultType === "mutation" || data.status === "repaired";
}

async function callReadUri(uri) {
  const res = await fetch("/api/uri/call", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uri, readonly: false, dry_run: false, approved: false, policy: "dev" }),
  });
  const data = await res.json();
  renderUriResult(data);
}

async function previewUri(event, uri) {
  event.preventDefault();
  const res = await fetch("/api/uri/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uri, policy: "dev" }),
  });
  const data = await res.json();
  renderUriResult(data);
  return false;
}

async function submitUriCall(event, form) {
  event.preventDefault();
  const uri = form.querySelector('input[name="uri"]').value;
  const approve = event.submitter && event.submitter.value === "approve";
  const res = await fetch("/api/uri/call", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      uri,
      approved: approve,
      dry_run: !approve,
      policy: "dev",
    }),
  });
  const data = await res.json();
  renderUriResult(data);
  if (shouldRefreshPage(data, { approved: approve })) {
    window.location.reload();
  }
  return false;
}
