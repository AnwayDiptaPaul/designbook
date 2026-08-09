# DesignBook - RCC Structural Design Application

A comprehensive, containerized Structural Engineering platform tailored for BNBC 2020 and ACI 318-19.
Integrates finite element arrays via Python wrappers against OpenSeesPy and computes member design reinforcement, limits states, and material BOQ mapping.

## Technology Stack

### Backend
- **FastAPI**: Asynchronous Python API.
- **OpenSeesPy**: Finite Element analysis solver.
- **Celery / Redis**: Async job queues for long-running nonlinear loops.
- **PostgreSQL**: Relational storage spanning elements and load permutations.

### Frontend
- **React 18 + TypeScript**: Client side UI. 
- **Vite**: Ultra-fast module bundler.
- **Tailwind CSS + shadcn/ui**: Modern component design system.
- **Zustand**: Cross-component reactive state modeling.

## Running the Application

### Method 1: Docker Compose (Production / Full Stack)
Brings up Nginx, the React frontend, the FastAPI backend, PostgreSQL database, and Redis/Celery queue.

```bash
cd app
# Copy environment file
cp .env.example .env

# Build and start all containers
docker-compose up --build -d
```
Access the application at `http://localhost`.

### Method 2: Local Development (Hot Reloading)

**Terminal 1: FastAPI Backend**
```bash
cd app/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2: React Frontend**
```bash
cd app/frontend
npm install
npm run dev
```
Access the application at `http://localhost:5173`.

## Module Directory

- `app/backend/core/analysis`: Contains `opensees_model`, `linear_elastic`, p-delta transformations.
- `app/backend/core/design`: Implements equations for ACI and BNBC reinforced concrete member capacity evaluations.
- `app/backend/core/loads`: Generates distributed combinations mapping against Dead, Live, Wind, and Seismic spectral accelerations.
- `app/backend/core/checks`: ACI 24 crack limiters and Branson effective inertia deflection algorithms.
- `app/backend/core/detailing`: Raw SVG generation rendering member structural blueprints.
- `app/frontend/src/pages`: 10 specialized interactive route nodes for the UI.
