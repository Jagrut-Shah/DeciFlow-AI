# DeciFlow AI: Local Setup Guide

Welcome to local development for DeciFlow AI. Follow these steps to get the environment running on your machine.

## Prerequisites
* Git
* Python 3.10+
* Node.js 18+
* Docker & Docker Compose (optional for local database/infra)

## Steps

**1. Clone the Repository**
Clone the project to your local machine and navigate into the directory:
```bash
git clone https://github.com/your-org/deciflow-ai.git
cd deciflow-ai
```

**2. Setup Environment Variables**
Copy the template variable file and configure it with your local credentials and API keys.
```bash
cp .env.example .env
```
Ensure you add your Google Cloud credentials and database keys inside the newly created `.env` file.

**3. Run the Backend (FastAPI)**
Navigate to the backend directory, install Python dependencies, and start the local development server:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The backend API will be available at `http://localhost:8000`.

**4. Run the Frontend (Next.js)**
Open a new terminal window, navigate to the frontend directory, install Node dependencies, and start the development server:
```bash
cd frontend
npm install
npm run dev
```
The web application will be accessible at `http://localhost:3000`.
