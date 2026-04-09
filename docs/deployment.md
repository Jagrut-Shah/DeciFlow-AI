# DeciFlow AI: Deployment Guide

DeciFlow AI utilizes a modern, serverless cloud deployment strategy to ensure scale, security, and performance.

## Backend Deployment (Google Cloud Run)
Our FastAPI backend is containerized and deployed to Google Cloud Run, allowing it to autoscale seamlessly based on incoming traffic.

1. The backend is built into a Docker container using `infra/docker/backend.Dockerfile`.
2. The image is pushed to Google Artifact Registry.
3. Cloud Run deploys the image, connecting it securely to BigQuery and Pub/Sub environments using the configurations stored in our `infra/terraform` directory.

## Frontend Deployment
The Next.js frontend is designed to be shipped globally via edge networks, deployed primarily to **Vercel** or **Firebase Hosting**.

* This provides out-of-the-box CDN edge caching.
* It automatically builds the Next.js app optimized for production speeds.

## Environment Variables Setup
Production environment variables must never be tracked in the repository. 
* **Backend**: Keys (like Database URLs and Vertex AI credentials) are injected natively via Google Cloud Secret Manager.
* **Frontend**: Keys (like Public API URLs) are managed natively via Vercel/Firebase environment settings in the cloud dashboard.

## Global CI/CD Flow
DeciFlow AI implements an automated Continuous Integration and Continuous Deployment (CI/CD) pipeline using GitHub Actions (`infra/ci-cd/github_actions.yml`).

1. **Push/PR**: Code pushed to the repository triggers automated unit and integration tests.
2. **Build**: Upon merging to `main`, Docker images and Next.js builds are automatically compiled.
3. **Deploy**: 
   * If tests pass, GitHub Actions triggers the deployment webhook to Vercel (for frontend) and updates the Cloud Run revision (for backend).
