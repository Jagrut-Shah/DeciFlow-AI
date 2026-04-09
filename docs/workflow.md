# DeciFlow AI: Development Workflow

To maintain a high standard of code quality and prevent merge conflicts, all developers must strictly adhere to the following Git workflow.

## 1. Create a Branch
Before writing any code, pull the latest changes from the `main` branch and create a new feature branch.
```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

## 2. Develop the Feature
Write your code, following the strict project rules, architecture patterns, and the API contracts. Commit your changes logically as you make progress.
```bash
git add .
git commit -m "Add descriptive message of the change"
```

## 3. Test Locally
Before submitting your work, ensure you test it locally.
* Run unit tests (`pytest` for backend, `jest` for frontend).
* Ensure there are no compilation or runtime errors.

## 4. Create a Pull Request (PR)
Push your feature branch to the remote repository and open a Pull Request (PR) targeting the `main` branch.
```bash
git push origin feature/your-feature-name
```
In the PR description, summarize your changes and link to any relevant task tracking tickets.

## 5. Merge After Approval
Wait for an automated CI check and a manual review from a team member. Once the PR is approved and all CI checks pass, it will be squashed and merged into `main`. Clean up by deleting your feature branch locally and remotely.
