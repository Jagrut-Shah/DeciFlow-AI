# DeciFlow AI – GitHub Workflow

I’ve created the GitHub repository for our project:
👉 [https://github.com/Jagrut-Shah/DeciFlow-AI.git](https://github.com/Jagrut-Shah/DeciFlow-AI.git)

## 🧱 1. Setup Project on Your System

**Step 1: Create a folder on your system**
Create any folder (e.g., `DeciFlow-AI`)

**Step 2: Open that folder in Antigravity**

## 📥 2. Clone the Repository

In your terminal:
```bash
git clone https://github.com/Jagrut-Shah/DeciFlow-AI.git
cd DeciFlow-AI
```
👉 This will automatically create the project folder with all files.

## 🔄 3. Get Latest Code

```bash
git checkout main
git pull origin main
```

---

## 🌿 4. Create Your Own Branch (VERY IMPORTANT)

```bash
git checkout -b feature/<role>-<name>
```

**Example:**
* `feature/frontend-richa`
* `feature/ai-jeenal`
* `feature/data-aarwa`

👉 **NEVER work on the `main` branch**

## 💻 5. Do Your Work

Work only in your assigned folders.

## 💾 6. Save Your Work (Commit)

```bash
git add .
git commit -m "what you implemented"
```

## ☁️ 7. Push Your Branch

```bash
git push origin feature/<your-branch-name>
```

👉 This will create your branch on GitHub.

## 🔁 8. Create Pull Request (PR)

* Go to GitHub.
* Click **Compare & pull request**.
* Base branch: `dev`
* Compare: `your branch`
* Click **Create pull request**.

👉 I will review and merge.

## 🔄 9. Development Flow

```plaintext
feature branch → PR → dev → (testing) → main
```

---

## ⚠️ RULES (STRICT)

**❌ Do NOT:**

* Push directly to `main`
* Use `git init` (the repository is already initialized)
* Work on someone else’s code without permission
* Add random libraries

**✅ Always:**

* Work in your branch
* Commit regularly
* Create a PR for your changes
* Follow the folder structure

## 🔐 SECURITY

* Do NOT upload API keys
* Use the `.env` file for secrets
* Keep code clean

## 🧠 FINAL FLOW

```plaintext
Create folder → Open → Clone → Create Branch → Work → Commit → Push → PR → Merge
```

If you have any confusion, ask before doing anything.

Let’s build this properly 🚀
