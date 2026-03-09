# Sprint Project 03 - FastAPI ML App

Build a microservices-based image classification system with FastAPI, Streamlit UI, and TensorFlow CNN model.

## Tech Stack

- **Python 3.8+** - Main programming language
- **FastAPI** - REST API framework
- **Streamlit** - Web UI
- **Redis** - Message queue for microservices communication
- **TensorFlow** - Pre-trained CNN model (1000+ categories)
- **PostgreSQL** - Database for users and feedback
- **Docker & Docker Compose** - Containerization and orchestration
- **Locust** - Stress testing
- **Pytest** - Testing framework
- **Black & isort** - Code formatting

## Setup & Run

1. Copy environment configuration:
```bash
cp .env.original .env
```

2. Create Docker network:
```bash
docker network create shared_network
```

3. Complete the Dockerfile in `api` folder (see `ASSIGNMENT.md`).

4. Start all services:
```bash
docker-compose up --build -d
```

5. Populate the database:
```bash
cd api
cp .env.original .env
docker-compose up --build -d
```

6. Stop services:
```bash
docker-compose down
```

**Note for Mac M1 users**: Use `model/Dockerfile.M1` for TensorFlow compatibility (see README for details).

## Access the Application

- **FastAPI Docs**: http://localhost:8000/docs
- **Web UI**: http://localhost:9090
- **Login credentials**: `admin@example.com` / `admin`

## Project Structure

```
├── api/                     # FastAPI backend (auth, model, feedback, user)
├── model/                   # ML service (TensorFlow CNN)
├── ui/                      # Streamlit web interface
├── stress_test/             # Locust performance tests
├── tests/                   # Integration tests
├── db_data/                 # PostgreSQL data
├── docker-compose.yml       # Service orchestration
├── ASSIGNMENT.md            # Detailed instructions
├── README.md
└── System_architecture_diagram.png
```

## Key Concepts Covered

- **Microservices Architecture** - Decoupled services communicating via Redis
- **REST API Design** - FastAPI endpoints with authentication
- **Async Processing** - Job queuing with Redis
- **Deep Learning Deployment** - Serving TensorFlow models in production
- **Containerization** - Multi-stage Docker builds
- **Authentication** - JWT-based user authentication
- **Database Design** - PostgreSQL with SQLAlchemy ORM
- **Stress Testing** - Performance analysis with Locust

## Business Problem

Automatically classify images into 1000+ categories using a pre-trained CNN model:
- Users upload images via web UI
- FastAPI receives and queues prediction jobs
- ML service processes images with TensorFlow
- Results returned to user with confidence scores
- Users can provide feedback on predictions

See `ASSIGNMENT.md` for complete implementation instructions and testing procedures.
