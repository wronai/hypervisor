async function callReadUri(uri) {
  const res = await fetch("/api/uri/call", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uri, readonly: false, dry_run: false, approved: false, policy: "dev" }),
  });
  const data = await res.json();
  document.getElementById("result").textContent = JSON.stringify(data, null, 2);
}

async function previewUri(event, uri) {
  event.preventDefault();
  const res = await fetch("/api/uri/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uri, policy: "dev" }),
  });
  const data = await res.json();
  document.getElementById("result").textContent = JSON.stringify(data, null, 2);
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
  document.getElementById("result").textContent = JSON.stringify(data, null, 2);
  return false;
}
