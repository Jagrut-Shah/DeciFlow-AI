# Developer Notes & Temporary Logic Tracker

This document tracks temporary implementations, mock data usage, and placeholder logic to ensure a clean transition from hackathon/MVP code to a production-grade system.

## 🛠️ Temporary Components

* **File**: [memory_queue.py](file:///c:/Users/HP/Downloads/DeciFlow%20AI/backend/app/infrastructure/queue/memory_queue.py)
  * **Reason**: Initial development speed; avoids infrastructure dependencies (Redis/RabbitMQ).
  * **To be replaced by**: Production-grade message broker (Redis + Celery or RabbitMQ).

* **File**: [result_store.py](file:///c:/Users/HP/Downloads/DeciFlow%20AI/backend/app/core/result_store.py)
  * **Reason**: Volatile storage for async results; loses all data on server reboot.
  * **To be replaced by**: Persistent state store (PostgreSQL or Redis with persistence).

* **File**: [main.py](file:///c:/Users/HP/Downloads/DeciFlow%20AI/backend/app/main.py) (Uptime Tracking)
  * **Reason**: Simple in-memory timestamp for `GET /status`.
  * **To be replaced by**: External monitoring service (Prometheus/Grafana) or database-backed logging.

* **File**: [dependencies.py](file:///c:/Users/HP/Downloads/DeciFlow%20AI/backend/app/core/dependencies.py)
  * **Reason**: Singletons for services are manually managed in the DI container.
  * **To be replaced by**: Robust DI framework or properly configured global state management.

## 📊 Test Data

* **Where used**: `AgentService` Registry
  * **Format**: In-memory Python objects.
  * **Replacement plan**: Load agent metadata from a configuration database or dynamic discovery service.

* **Where used**: `api/v1/endpoints/pipeline.py` (Mock Results)
  * **Format**: Static JSON/Dictionaries in `ResultStore`.
  * **Replacement plan**: Real pipeline outputs from agent execution nodes.

## 🧹 Cleanup Checklist

* [ ] **Persistence**: Replace `ResultStore` with persistent database integration.
* [ ] **Messaging**: Migrate `MemoryQueue` to Redis/RabbitMQ.
* [ ] **Auth**: Rotate `SECRET_KEY` and move to a Secret Manager (e.g., GCP Secret Manager).
* [ ] **Monitoring**: Integrate with centralized log aggregation (ELK/Sentry).
- [ ] **Data Cleanup**: Implement TTL logic for pipeline results to avoid memory bloating.
- [ ] **Logging**: Remove verbose debug logs in `WorkflowEngine` and `MemoryQueue`.

---
*Last Updated: 2026-04-10*
