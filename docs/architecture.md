# DeciFlow AI: Architecture Overview

DeciFlow AI operates on a robust, modular architecture designed for scalability, performance, and intelligent decision-making. The system utilizes modern web technologies and advanced machine learning to provide actionable insights.

## System Layers

Our architecture consists of the following distinct layers, ensuring clear separation of concerns:

* **Frontend Layer**: Built with Next.js, this layer provides a highly responsive, intuitive user interface for visualizing data, insights, and interacting with AI agents.
* **API Layer**: Powered by FastAPI, acting as the high-performance gateway connecting the frontend with backend services.
* **Application Layer**: Contains the core business logic, services, and orchestration workflows.
* **Decision Engine Layer**: The intelligence core that evaluates options, tests constraints, and ranks possibilities to generate optimal decisions.
* **AI Layer**: Houses our autonomous AI agents and integrates with Google Vertex AI for advanced generative capabilities structure and evaluations.
* **Data Layer**: Manages persistent storage and analytics through Google BigQuery and Cloud Storage.
* **Event Layer**: Utilizes Google Cloud Pub/Sub for asynchronous message passing and event-driven workflows.

## Deep Dive into Core Components

### Decision Intelligence Layer
The Decision Engine is tasked with evaluating complex business rules. It ingests data, considers constraints, and leverages our scoring mechanics to rank and recommend the most effective decisions.

### AI Agents
DeciFlow AI utilizes specialized autonomous agents:
* **Data Agent**: Cleans and normalizes incoming data.
* **Insight Agent**: Extracts meaningful trends.
* **Prediction Agent**: Forecasts future outcomes using ML models.
* **Decision Agent**: Synthesizes insights and predictions to propose actions.

### Data Flow
1. **Ingestion**: Raw data enters via the API or Event Layer.
2. **Processing**: The Data Agent normalizes it, storing it in BigQuery/Storage.
3. **Analysis**: Insight and Prediction Agents analyze the normalized data.
4. **Decision**: The Decision Engine evaluates the analysis and determines the best course of action.
5. **Presentation**: Results are delivered securely back to the frontend.
