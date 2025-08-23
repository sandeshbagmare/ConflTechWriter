# AI Technical Article Generation System

A production-grade, multi-agent AI system for creating fact-backed technical articles with transparent citations and verification.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for research, analysis, writing, and quality assurance
- **Fact-Backed Content**: Every claim is linked to verifiable sources
- **Real-Time Information**: Uses live web search for current information
- **Quality Assurance**: Fact-checking, adversarial review, and editorial refinement
- **Interactive Evidence Trail**: Click any citation to see the source
- **Visual Aids**: Automatic generation of diagrams and charts
- **Scalable Content**: Generate articles of 5,000+ words

## 🏗️ Architecture

The system uses a multi-agent workflow orchestrated by LangGraph:

```mermaid
graph TD
    A[Chief Researcher] --> B[Search Agents]
    B --> C[Analyst Agents]
    C --> D[Writer Agent]
    D --> E[QA Trinity]
    E --> F[Visualizer Agent]
    F --> G[Finalizer Agent]
    E -->|Needs Revision| D
    E -->|Needs More Info| B
```

### Core Agents

1. **Chief Researcher**: Breaks down topics into structured research plans
2. **Search Agents**: Find relevant and credible sources
3. **Analyst Agents**: Extract factual snippets from sources
4. **Writer Agent**: Synthesize information into coherent narrative
5. **QA Trinity**: Fact-checker, adversarial critic, and editor
6. **Visualizer Agent**: Create diagrams and charts
7. **Finalizer Agent**: Package the complete article

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Orchestration**: LangGraph for workflow management
- **Database**: PostgreSQL with pgvector
- **Cache/Queue**: Redis + Celery
- **LLM**: Google Gemini API
- **Search**: Google Custom Search API
- **Scraping**: BeautifulSoup4 + Playwright
- **Frontend**: React + Next.js (planned)
- **Deployment**: Docker + Kubernetes

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API key
- Google Custom Search API key and Engine ID

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ContentCreation

# Copy environment template
cp .env.template .env

# Edit .env with your API keys
# At minimum, set:
# GEMINI_API_KEY=your-key-here
# GOOGLE_SEARCH_API_KEY=your-key-here
# GOOGLE_SEARCH_ENGINE_ID=your-engine-id
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### 3. Verify Installation

```bash
# Health check
curl http://localhost:8000/health/

# Detailed health check
curl http://localhost:8000/health/detailed
```

### 4. Generate Your First Article

```bash
# Create an article generation job
curl -X POST "http://localhost:8000/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Vector Databases",
    "desired_depth": "intermediate",
    "max_length": 5000
  }'

# Response will include a job_id
# {"job_id": "123e4567-e89b-12d3-a456-426614174000", "status": "queued"}

# Check job status
curl http://localhost:8000/v1/jobs/123e4567-e89b-12d3-a456-426614174000

# Get final article (when completed)
curl http://localhost:8000/v1/jobs/123e4567-e89b-12d3-a456-426614174000/artifacts
```

## 📁 Project Structure

```
ContentCreation/
├── backend/
│   ├── app/
│   │   ├── agents/          # Individual agent implementations
│   │   ├── api/             # FastAPI routes
│   │   ├── core/            # Configuration and database
│   │   ├── graph/           # LangGraph workflow definitions
│   │   ├── models/          # Pydantic schemas and SQLAlchemy models
│   │   ├── services/        # External service wrappers
│   │   ├── workers/         # Celery task definitions
│   │   └── main.py          # FastAPI application entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React frontend (to be implemented)
├── deployment/              # Kubernetes manifests
├── docs/                    # Documentation
├── docker-compose.yml       # Development environment
└── README.md
```

## 🧪 Development

### Running Tests

```bash
# Install development dependencies
pip install -r backend/requirements.txt

# Run tests
cd backend
pytest tests/ -v --cov=app

# Type checking
mypy app/

# Code formatting
black app/
isort app/
```

### Database Migrations

```bash
# Generate migration
cd backend
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Monitoring

- **API Documentation**: http://localhost:8000/docs
- **Celery Monitoring**: http://localhost:5555 (Flower)
- **Redis**: redis-cli -h localhost -p 6379
- **PostgreSQL**: psql -h localhost -U aiuser -d ai_articles

## 🔧 Configuration

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GOOGLE_SEARCH_API_KEY` | Google Search API key | Required |
| `MAX_ARTICLE_LENGTH` | Maximum words per article | 10000 |
| `FACT_CHECK_THRESHOLD` | Minimum confidence for verification | 0.8 |
| `MAX_JOBS_PER_USER_PER_HOUR` | Rate limiting | 5 |

## 🌐 API Reference

### Create Article Job

```http
POST /v1/jobs
Content-Type: application/json

{
  "topic": "Your article topic",
  "desired_depth": "beginner|intermediate|expert",
  "max_length": 5000,
  "include_visuals": true
}
```

### Check Job Status

```http
GET /v1/jobs/{job_id}
```

### Get Final Article

```http
GET /v1/jobs/{job_id}/artifacts
```

### Submit Feedback

```http
POST /v1/jobs/{job_id}/feedback
Content-Type: application/json

{
  "rating": 5,
  "comment": "Excellent article!",
  "feedback_type": "general"
}
```

## 🚀 Production Deployment

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f deployment/

# Scale workers
kubectl scale deployment celery-worker --replicas=5

# Monitor
kubectl get pods -w
```

### Environment Variables for Production

```bash
# Security
DEBUG=false
SECRET_KEY=<strong-random-key>

# Database
DATABASE_URL=postgresql://user:pass@prod-db:5432/ai_articles

# Monitoring
ENABLE_TRACING=true
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](./docs/)
- [API Reference](http://localhost:8000/docs)
- [Architecture Guide](./docs/architecture.md)
- [Development Setup](./docs/development.md)

## 🏆 Roadmap

- [ ] **Phase 1**: Core agent implementation ✅
- [ ] **Phase 2**: Quality assurance loop
- [ ] **Phase 3**: React frontend
- [ ] **Phase 4**: Production hardening
- [ ] **Phase 5**: Advanced features (user accounts, templates, etc.)

---

**Built with ❤️ for creating high-quality, fact-based technical content.**
