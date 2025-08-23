# AI Technical Article Generation System - Copilot Instructions

This is an advanced AI-powered technical article generation system built with a multi-agent architecture.

## Project Overview
- **Backend**: FastAPI with Python 3.11+
- **AI Orchestration**: LangGraph for multi-agent workflow management
- **Task Queue**: Celery with Redis broker
- **Database**: PostgreSQL with pgvector
- **Frontend**: React with Next.js
- **LLM Integration**: Google Gemini API
- **Deployment**: Docker + Kubernetes

## Architecture
The system uses a multi-agent approach with specialized agents:
- Chief Researcher Agent (planning)
- Search Agents (information retrieval)
- Analyst Agents (content extraction)
- Writer Agent (synthesis)
- QA Trinity (fact-checking, critique, editing)
- Visualizer Agent (diagrams/charts)
- Finalizer Agent (packaging)

## Development Guidelines
- Follow structured data patterns with Pydantic models
- Implement robust error handling and retry logic
- Use async/await patterns for I/O operations
- Maintain strong typing throughout the codebase
- Focus on observability and monitoring

## Checklist Progress
- [x] Project structure created
- [x] Core dependencies defined (requirements.txt)
- [x] Database schema implemented (SQLAlchemy models)
- [x] Basic agent implementations (Chief Researcher, LLM Service)
- [x] API endpoints (FastAPI routes for jobs and health)
- [x] Orchestration workflow (LangGraph-based)
- [x] Docker configuration (Dockerfile, docker-compose.yml)
- [x] Environment configuration (.env.template)
- [x] Documentation (comprehensive README.md)
- [ ] Frontend development (React/Next.js - planned)
- [ ] Testing suite (pytest configuration)
- [ ] Production deployment (Kubernetes manifests)
