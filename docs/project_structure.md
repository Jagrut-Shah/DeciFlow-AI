# DeciFlow AI: Project Structure

Our codebase is organized into modular directories to ensure scalability, clean architecture, and easy team coordination.

## Top-Level Directories

### backend
Contains the core Python FastAPI application. It is structured using Clean Architecture principles, dividing responsibilities into API routes, core configuration, domains, models, repositories, services, workflows, and the decision engine. All backend business logic lives here.

### frontend
Houses the Next.js web application. It includes isolated React components, custom hooks, global state stores, and service integrations required to provide a seamless user interface.

### ml
The machine learning hub of the project. It stores data pipelines, evaluation metrics, feature store configurations, experiment tracking, and our specialized models for forecasting, anomaly detection, and segmentation.

### infra
Contains Infrastructure as Code (IaC) and containerization rules. This includes Terraform configurations for Google Cloud Platform (Cloud Run, BigQuery, Pub/Sub), Dockerfiles for building our services, and CI/CD pipelines.

### scripts
A collection of utility and operational scripts to aid development and deployment. This includes database migration automation, data seeding scripts, and local execution runners.

### tests
The application-wide test suite. It is divided into unit tests for isolated functionality, integration tests for cross-component interactions, and end-to-end (e2e) tests to validate full user flows.
