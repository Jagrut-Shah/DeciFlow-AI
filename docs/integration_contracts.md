# DeciFlow AI — Integration Contracts

> **Owner:** Backend Lead (Jagrut)
> **Last Updated:** April 2026
> This document is the single source of truth for all inter-team API contracts.
> Breaking changes require explicit approval and a version bump.

---

## 📌 For Aarwa (Data Engineer)

### What format does `DataService` expect?

The entry point for all data is:

```python
DataService.process_raw_data(source: str, payload: Dict[str, Any]) -> Dict[str, Any]
```

**`source`** — Label identifying who sent the data (e.g. `"bigquery"`, `"upload"`, `"api"`).

**`payload`** — A flat or nested dict of raw field values. Example:

```json
{
  "revenue": 15000.5,
  "user_count": 300,
  "churn_rate": 0.08,
  "region": "APAC",
  "product_active": true
}
```

**Rules:**
- ✅ String values will be stripped of whitespace automatically
- ✅ Empty payload `{}` is safe — returns fallback, never crashes
- ❌ Do NOT send nested arrays of objects (flatten to top-level fields)
- ❌ Do NOT send null values — omit the field entirely if no value

**Output you can expect:**

```json
{
  "source": "bigquery",
  "record_count": 5,
  "fields": ["revenue", "user_count", "churn_rate", "region", "product_active"],
  "raw": { ...sanitized payload... },
  "_fallback": false
}
```

`_fallback: true` means the payload was empty or invalid — downstream steps will gracefully skip.

---

### What data types are valid?

| Type | Example | Behavior |
|---|---|---|
| `int` / `float` | `"revenue": 500.0` | Extracted as numeric feature |
| `bool` | `"active": true` | Extracted as boolean feature |
| `str` | `"region": "APAC"` | Extracted as text feature |
| `dict` | `"meta": {...}` | String values inside stripped; numerics ignored |

---

## 📌 For Jeenal (AI Agents Engineer)

### How are agents called?

All agents are dispatched through:

```python
await AgentService.execute_agent(agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]
```

**`agent_name`** — One of the registered agent names (see below).

**`context`** — Dict with standard fields:

```json
{
  "session_id": "uuid-string",
  "pipeline_stage": "InsightGeneration",
  "payload": {
    "revenue": 15000.5,
    "region": "APAC"
  }
}
```

---

### Registered Agents

| Agent Name | Purpose | Called By |
|---|---|---|
| `data_analyst` | Validates and summarizes raw data quality | DataService (optional hook) |
| `insight_generator` | Generates structured insights from features | InsightService (optional hook) |
| `decision_advisor` | Provides advisory reasoning for decisions | DecisionService (optional hook) |
| `risk_assessor` | Assesses risk of a proposed action | SimulationService (optional hook) |

---

### Output contract every agent MUST return

```python
{
    "agent_name": str,              # must echo the input agent_name
    "status": "success" | "unavailable" | "error",
    "result": Dict[str, Any],       # see per-agent schema below
    "error": str | None             # None on success
}
```

**⚠️ Rule: agents MUST NOT raise exceptions. Always return the dict above.**

---

### Per-Agent `result` Schemas

#### `data_analyst`
```json
{
  "summary": "Analyzed payload with 5 fields.",
  "record_count": 5,
  "quality_score": 0.85
}
```

#### `insight_generator`
```json
{
  "key_insights": ["Trend is upward", "Anomaly in revenue"],
  "confidence": 0.78
}
```

#### `decision_advisor`
```json
{
  "recommendation": "PROCEED",
  "risk": "medium"
}
```

#### `risk_assessor`
```json
{
  "risk_level": "medium",
  "risk_score": 0.45,
  "flags": []
}
```

---

### How to register a new agent

In `app/services/agent_service.py`, add to `_AGENT_REGISTRY`:

```python
def my_new_agent(context: Dict[str, Any]) -> Dict[str, Any]:
    # implement logic using context["payload"]
    return {"key": "value"}

_AGENT_REGISTRY["my_agent_name"] = my_new_agent
```

That's it. The dispatcher and fallback handling is already built.

---

## 📌 API Endpoints Summary

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | None | Service health check |
| `GET` | `/metrics` | None | In-memory metrics snapshot |
| `POST` | `/api/v1/decisions/decide` | Bearer JWT | Run decision engine directly |
| `POST` | `/api/v1/pipeline/run` | Bearer JWT | Enqueue async pipeline (202) |
| `POST` | `/api/v1/pipeline/run-sync` | Bearer JWT | Run pipeline synchronously |
| `GET` | `/api/v1/pipeline/status` | Bearer JWT | Pipeline metrics snapshot |

---

## 📌 Pipeline Flow

```
POST /pipeline/run-sync
        │
        ▼
 WorkflowEngine.execute_pipeline(session_id, payload)
        │
        ├─ Step 1: DataService.process_raw_data()     ← Aarwa provides data format
        ├─ Step 2: FeatureService.extract_features()
        ├─ Step 3: InsightService.generate_insights()  ← Jeenal: insight_generator agent called here
        ├─ Step 4: PredictionService.predict()
        ├─ Step 5: DecisionService.orchestrate_decision()
        │           └─ DecisionIntelligenceEngine
        │               ├─ DefaultGenerator.generate()
        │               ├─ DefaultConstraintEngine.filter()
        │               ├─ DefaultScorer.score()
        │               ├─ DefaultRanker.rank()
        │               └─ DefaultExplainer.explain()
        └─ Step 6: SimulationService.simulate()        ← Jeenal: risk_assessor agent called here
```

---

## 📌 Authentication

All protected endpoints require a Bearer JWT:

```
Authorization: Bearer <token>
```

Token payload:
```json
{
  "sub": "user_id",
  "role": "user | admin",
  "type": "access",
  "exp": 1712345678
}
```

Generate a token via the auth service (or use `create_access_token()` in `security.py` for testing).

---

## 📌 Error Response Format

All errors follow:

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "meta": {
    "error_code": "TOKEN_EXPIRED | UNAUTHORIZED | FORBIDDEN | ...",
    "path": "/api/v1/...",
    "trace_id": "uuid"
  }
}
```

Use `trace_id` to correlate with server logs when debugging.
