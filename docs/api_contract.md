# DeciFlow AI — API Contract
**Version:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Authentication:** Bearer JWT (all `/api/v1/` endpoints)

> This document supersedes all previous versions. All endpoints listed here are implemented and tested.

---

## Authentication

All API v1 endpoints require a valid Bearer JWT:

```
Authorization: Bearer <access_token>
```

**Token payload:**
```json
{
  "sub": "user_id",
  "role": "user | admin",
  "type": "access",
  "exp": 1712345678
}
```

---

## System Endpoints (No Auth Required)

### `GET /health`
Health check. Always returns 200 if the backend is running.

**Response:**
```json
{
  "status": "success",
  "data": {
    "service": "DeciFlow AI",
    "status": "operational",
    "version": "1.0.0",
    "env": "development"
  },
  "message": "Backend is healthy and operational."
}
```

---

### `GET /metrics`
Returns in-process performance metrics. Admin role recommended.

**Response:**
```json
{
  "status": "ok",
  "metrics": {
    "counters": {
      "requests_total": 42,
      "pipeline_executions_total": 5,
      "pipeline_success_total": 4
    },
    "latencies": {
      "request_latency_ms": {
        "count": 42,
        "avg_ms": 38.5,
        "p50_ms": 31.0,
        "p95_ms": 89.2,
        "p99_ms": 120.1,
        "max_ms": 145.3
      }
    }
  }
}
```

---

## Decision Engine (`/api/v1/decisions`)

### `POST /api/v1/decisions/decide`

Directly invokes the DecisionIntelligenceEngine.

**Request:**
```json
{
  "session_id": "session-abc-123",
  "payload": {
    "revenue": 15000.5,
    "churn_rate": 0.08,
    "region": "APAC"
  },
  "mode": "standard"
}
```

**Response (`200 OK`):**
```json
{
  "status": "success",
  "data": {
    "action": "REDUCE_PRICE",
    "confidence_score": 0.80,
    "score": 0.504,
    "impact": 0.8,
    "feasibility": 0.7,
    "explanation": "Action 'REDUCE_PRICE' selected due to score of 0.50 from 0.8 impact and 0.9 confidence.",
    "alternatives": [],
    "trace_id": "uuid",
    "is_fallback": false
  }
}
```

---

## Pipeline (`/api/v1/pipeline`)

### `POST /api/v1/pipeline/run`
Enqueues the full pipeline for background async execution.

**Request:**
```json
{
  "session_id": "session-abc-123",
  "payload": {
    "revenue": 15000.5,
    "users": 300,
    "region": "APAC"
  }
}
```

**Response (`202 Accepted`):**
```json
{
  "status": "success",
  "data": {
    "task_id": "uuid",
    "session_id": "session-abc-123",
    "status": "queued",
    "trace_id": "uuid",
    "message": "Pipeline task enqueued successfully."
  }
}
```

---

### `POST /api/v1/pipeline/run-sync`
Runs the full pipeline synchronously. Returns complete result.

**Request:** Same as `/run`.

**Response (`200 OK`):**
```json
{
  "status": "success",
  "data": {
    "session_id": "session-abc-123",
    "trace_id": "uuid",
    "stages": {
      "data": {"source": "workflow_engine", "record_count": 3, "fields": ["revenue", "users", "region"], "_fallback": false},
      "features": {"numeric": {"revenue": 15000.5, "users": 300.0}, "boolean": {}, "text": {"region": "APAC"}, "feature_count": 3, "_fallback": false},
      "insights": {"insights_summary": "Analyzed 3 features. Top signal: 'revenue'. Confidence: 30%.", "confidence": 0.3, ...},
      "predictions": {"prediction_score": 0.3, "confidence": 0.3, "probabilities": {"positive": 0.3, "negative": 0.7}},
      "decisions": {"action": "REDUCE_PRICE", "score": 0.504, "confidence": 0.9, "explanation": "...", "_fallback": false},
      "simulation": {"projected_roi": 0.94, "risk_level": "high", "recommendation": "...", "_fallback": false}
    }
  }
}
```

---

### `GET /api/v1/pipeline/status`
Returns pipeline metrics snapshot.

**Response (`200 OK`):** Same structure as `GET /metrics`.

---

## Error Response Format

All errors follow a consistent structure:

```json
{
  "status": "error",
  "message": "Human-readable error description.",
  "meta": {
    "error_code": "TOKEN_EXPIRED | UNAUTHORIZED | FORBIDDEN | BAD_REQUEST | INTERNAL_SERVER_ERROR",
    "path": "/api/v1/decisions/decide",
    "trace_id": "uuid"
  }
}
```

| HTTP Code | `error_code` | Cause |
|---|---|---|
| 401 | `TOKEN_EXPIRED` | JWT expired |
| 401 | `TOKEN_INVALID` | Bad signature or malformed |
| 401 | `TOKEN_MALFORMED` | Missing `sub` claim |
| 401 | `TOKEN_TYPE_MISMATCH` | Refresh token used as access token |
| 403 | `FORBIDDEN` | Role not sufficient |
| 400 | `BAD_REQUEST` | Validation failure |
| 500 | `INTERNAL_SERVER_ERROR` | Unhandled exception (safe response, no trace leak) |

---

## Response Envelope

All responses use a standard envelope:

```json
{
  "status": "success | error",
  "data": {},
  "message": "Optional description"
}
```

---

## Stale / Removed Endpoints

The following endpoints were in the previous version of this document and **do not exist**:

| Old Endpoint | Status | Replacement |
|---|---|---|
| `POST /upload` | ❌ Not implemented | Aarwa's data team responsibility |
| `GET /insights` | ❌ Not implemented | Use `POST /pipeline/run-sync` |
| `GET /predictions` | ❌ Not implemented | Use `POST /pipeline/run-sync` |
| `GET /decisions` | ❌ Not implemented | Use `POST /api/v1/decisions/decide` |
| `POST /simulation` | ❌ Not implemented | Included in pipeline output |
| `POST /chat` | ❌ Not implemented | Jeenal's AI agent responsibility |
