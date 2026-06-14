# Markpact: Chat UI connected to Taskinity API

## Intent

Create a simple chat-style UI for users who do not want to learn every URI command first.

## User command

```text
pokaż proces agenta weather-map-agent.local
```

## System behavior

1. Convert natural language to URI.
2. Explain the selected URI.
3. Call the runtime API.
4. Render the result as a chat answer.
5. Show technical envelope only in inspector.

## Required API

```http
POST /api/nl/ask
POST /api/uri/call
GET /health
```

## Required envelope fields

```json
{
  "ok": true,
  "workflow_status": "completed",
  "execution_status": "completed",
  "service_result_status": "succeeded",
  "result_type": "process_view",
  "data": {},
  "meta": {}
}
```

## UX acceptance criteria

- User sees a chat message, not raw JSON.
- User can set API base URL.
- UI has mock fallback.
- Each action still maps to a URI.
- Mutating actions are visible as repair/ticket/evolution steps.
