# DeciFlow AI: Strict Project Rules

> [!CAUTION]
> **VERY IMPORTANT:** These rules are mandatory for all team members. Failure to comply will block deployments and pull requests.

## Code Rules

* **No direct push to the main branch.** The main branch is locked for direct commits.
* **Use feature branches.** Always create a new branch for your work (e.g., `feature/data-pipeline` or `fix/button-styling`).
* **Pull requests are required.** Every code change must be reviewed via a Pull Request (PR) before being merged into main.

## Tech Stack Rules

* **Backend Constraint:** Use **FastAPI only**. Do not introduce alternative frameworks like Flask or Django.
* **Frontend Constraint:** Use **Next.js only**.
* **Library Approvals:** Do NOT install or add random third-party libraries (NPM or pip packages) without team approval.
* **Folder Structure:** Code must be placed in the designated folder structure. Do not invent new structures outside of the provided layout.

## Collaboration Rules

* **Daily Updates:** Provide brief updates on your progress daily to ensure team synchronization.
* **Code Ownership:** Do NOT modify another team member's code domain without explicit permission.
* **API Compliance:** You must strictly conform to the schemas defined in `api_contract.md`. If an API contract needs to change, it requires cross-team coordination.

## Security Rules

* **No Hardcoded Keys:** NEVER hardcode or commit API keys, database passwords, or secrets to the repository.
* **Use Environment Variables:** All sensitive data must be read exclusively from `.env` files locally and Secret Manager in production.
* **Input Validation:** All incoming data on the backend must be strictly validated (using Pydantic, for example) to prevent injection and security flaws.
