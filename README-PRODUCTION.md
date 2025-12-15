# Production-Grade Networking Demo Platform

A secure, containerized web platform for running networking demonstrations in isolated environments. Built with modern best practices, defense-in-depth security, and production-ready architecture.

## 🎯 Overview

This platform transforms educational networking scripts into a production-ready web application where users can:
- Browse available networking demos (Layer 2-4)
- Execute demos with validated parameters via web UI
- View structured JSON results in real-time
- All execution happens in isolated Docker containers with strict security constraints

**Key Features:**
- ✅ No arbitrary code execution - only predefined demos
- ✅ Strong input validation with Pydantic schemas
- ✅ Docker container isolation per job
- ✅ Resource limits (CPU, memory, execution time)
- ✅ Async job queue with Redis + RQ
- ✅ Modern React frontend
- ✅ FastAPI backend with OpenAPI documentation
- ✅ Comprehensive security controls

## 📋 Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

**High-Level Components:**
```
Frontend (React) → API (FastAPI) → Queue (Redis) → Worker → Isolated Containers
```

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- Linux (recommended) or macOS

### Setup and Run

1. **Clone the repository:**
```bash
git clone <repository-url>
cd practical-networking-from-zero-to-hero
```

2. **Build and start all services:**
```bash
docker-compose up --build
```

This will start:
- Redis (port 6379)
- FastAPI backend (port 8000)
- RQ Worker
- React frontend (port 3000)

3. **Access the platform:**
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/api/health

## 🔧 Development Setup

### Backend Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-backend.txt

# Run FastAPI server locally
cd /path/to/repo
PYTHONPATH=. uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run worker (requires Redis)
PYTHONPATH=. rq worker --url redis://localhost:6379/0 default
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Testing a Demo Locally

You can test demos directly without the full stack:

```bash
# Activate virtual environment
source venv/bin/activate

# Test TCP handshake demo
sudo python3 -m backend.demos.layer4.tcp_handshake
```

## 📚 API Documentation

### Endpoints

**Demos:**
- `GET /api/demos` - List all available demos
- `GET /api/demos/{demo_id}` - Get demo details and parameter schema

**Jobs:**
- `POST /api/jobs` - Submit a new demo execution job
- `GET /api/jobs/{job_id}` - Get job status and results

**Health:**
- `GET /api/health` - Health check

### Example API Usage

```bash
# List available demos
curl http://localhost:8000/api/demos

# Get specific demo
curl http://localhost:8000/api/demos/tcp-handshake

# Submit a job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "demo_id": "tcp-handshake",
    "parameters": {
      "target_ip": "142.250.185.46",
      "target_port": 80,
      "timeout": 5
    }
  }'

# Check job status (replace {job_id} with actual ID)
curl http://localhost:8000/api/jobs/{job_id}
```

## 🔒 Security Model

### Defense in Depth

**Layer 1: Input Validation**
- Strict Pydantic schemas for all parameters
- Type checking, range validation, regex patterns
- Whitelist approach - only known fields accepted

**Layer 2: Demo Registry**
- Only predefined demos can be executed
- No eval(), exec(), or dynamic imports
- Parameters are data only, never code

**Layer 3: Container Isolation**
- Non-root user (UID 1000)
- Read-only root filesystem
- Limited writable /tmp
- No privilege escalation
- All capabilities dropped

**Layer 4: Resource Limits**
- CPU: 1 core maximum
- Memory: 512MB maximum
- Processes: 100 maximum
- Execution timeout: 30-60 seconds
- Network: disabled by default

**Layer 5: Monitoring**
- All requests logged
- Job execution tracked
- Failed attempts logged
- Resource usage monitored

### Container Security Configuration

```yaml
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
read_only: true
cpus: '1.0'
mem_limit: 512m
pids_limit: 100
network_mode: none
```

## 🎨 Adding New Demos

### Step 1: Create Demo Function

Create a new file in the appropriate layer directory:

```python
# backend/demos/layer4/my_demo.py
from typing import Dict, Any
from backend.schemas.demos import MyDemoParams

def execute_my_demo(params: MyDemoParams) -> Dict[str, Any]:
    """
    Execute my custom demo.
    
    Returns structured JSON output.
    """
    # Implementation here
    return {
        "success": True,
        "data": {
            "result": "Demo output here"
        },
        "error": None,
        "metadata": {
            "demo_version": "1.0.0"
        }
    }
```

### Step 2: Define Parameter Schema

Add to `backend/schemas/demos.py`:

```python
class MyDemoParams(BaseModel):
    """Parameters for my demo."""
    
    parameter1: str = Field(
        ...,
        description="Description of parameter1",
        examples=["example-value"]
    )
    parameter2: int = Field(
        default=10,
        description="Description of parameter2",
        ge=1,
        le=100
    )
    
    @field_validator("parameter1")
    @classmethod
    def validate_parameter1(cls, v: str) -> str:
        # Custom validation logic
        if not v.startswith("valid-"):
            raise ValueError("Must start with 'valid-'")
        return v
```

### Step 3: Register Demo

Add to `backend/demos/registry.py` in the `_initialize_demos` method:

```python
self.register(
    DemoRecipe(
        id="my-demo",
        name="My Custom Demo",
        description="Detailed description of what the demo does",
        category="layer4",
        max_runtime=30,
        requires_network=False,
        requires_root=False,
        parameters_schema=MyDemoParams.model_json_schema()
    ),
    execute_my_demo,
    MyDemoParams
)
```

### Step 4: Test

```bash
# Test the demo function directly
python3 -c "
from backend.demos.registry import get_registry
result = get_registry().execute_demo('my-demo', {
    'parameter1': 'valid-test',
    'parameter2': 20
})
print(result)
"

# Test via API
docker-compose restart api worker
# Use frontend or curl to test
```

That's it! The demo is now available through the API and frontend.

## 📂 Project Structure

```
.
├── ARCHITECTURE.md           # Detailed architecture documentation
├── README.md                 # Original educational README
├── README-PRODUCTION.md      # This file
├── docker-compose.yml        # Orchestration configuration
├── requirements.txt          # Core Python dependencies
├── requirements-backend.txt  # Backend-specific dependencies
│
├── api/                      # FastAPI application
│   ├── main.py              # FastAPI app and configuration
│   └── routers/             # API route handlers
│       ├── demos.py         # Demo listing endpoints
│       └── jobs.py          # Job submission and status
│
├── backend/                  # Business logic and execution
│   ├── schemas/             # Pydantic data models
│   │   ├── base.py          # Base schemas
│   │   └── demos.py         # Demo parameter schemas
│   ├── demos/               # Demo implementations
│   │   ├── registry.py      # Demo registration system
│   │   ├── layer2/          # Layer 2 demos
│   │   ├── layer3/          # Layer 3 demos
│   │   └── layer4/          # Layer 4 demos
│   │       └── tcp_handshake.py  # Example demo
│   └── worker/              # Job execution
│       ├── queue_manager.py # Redis queue management
│       ├── executor.py      # Container orchestration
│       └── container_runner.py  # In-container execution
│
├── frontend/                 # React application
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── DemoList.js  # Demo selection
│   │   │   ├── DemoExecutor.js  # Parameter input
│   │   │   └── JobStatus.js # Result display
│   │   ├── services/        # API client
│   │   │   └── api.js
│   │   ├── App.js           # Main app component
│   │   └── index.js         # Entry point
│   └── package.json         # npm dependencies
│
├── docker/                   # Docker configurations
│   ├── Dockerfile.api       # API container
│   ├── Dockerfile.worker    # Worker container
│   ├── Dockerfile.frontend  # Frontend container
│   └── nginx.conf           # Nginx configuration
│
├── layer2/                   # Original demo scripts
├── layer3/                   # (Maintained for reference)
├── layer4/                   # (Can still be run directly)
├── application/
└── tools/
```

## 🧪 Testing

### Manual Testing

1. **Test Backend API:**
```bash
# Health check
curl http://localhost:8000/api/health

# List demos
curl http://localhost:8000/api/demos

# Submit job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"demo_id": "tcp-handshake", "parameters": {"target_ip": "8.8.8.8", "target_port": 80, "timeout": 5}}'
```

2. **Test Frontend:**
- Open http://localhost:3000
- Click on a demo
- Fill in parameters
- Submit and watch results

3. **Test Worker:**
```bash
# Check worker logs
docker-compose logs -f worker

# Verify Redis connection
docker-compose exec redis redis-cli ping
```

### Automated Tests (Future)

```bash
# Run backend tests
pytest tests/

# Run frontend tests
cd frontend && npm test
```

## 📊 Monitoring and Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f frontend

# Follow logs in real-time
docker-compose logs -f --tail=100
```

### Health Checks

```bash
# API health
curl http://localhost:8000/api/health

# Redis health
docker-compose exec redis redis-cli ping

# Check all containers
docker-compose ps
```

## 🔧 Troubleshooting

### Common Issues

**1. Port already in use:**
```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
sudo lsof -i :8000
sudo lsof -i :3000
```

**2. Permission denied when running demos:**
- Demos requiring raw packet access need root privileges
- This is handled automatically in Docker containers
- For local testing, use `sudo python3 ...`

**3. Worker not processing jobs:**
```bash
# Check Redis connection
docker-compose exec worker python -c "import redis; r = redis.from_url('redis://redis:6379/0'); print(r.ping())"

# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker
```

**4. Frontend can't connect to API:**
- Check API is running: http://localhost:8000/api/health
- Check CORS configuration in `api/main.py`
- Check network in docker-compose.yml

## 🚀 Production Deployment

### Considerations

1. **Use Kubernetes** for orchestration
2. **Redis Cluster** for high availability
3. **Multiple worker replicas** for scalability
4. **HTTPS/TLS** termination at load balancer
5. **Authentication** and rate limiting
6. **Centralized logging** (ELK, CloudWatch, etc.)
7. **Monitoring** (Prometheus, Grafana)
8. **Secrets management** (Vault, AWS Secrets Manager)

### Environment Variables

```bash
# Production environment variables
REDIS_URL=redis://redis-cluster:6379/0
LOG_LEVEL=WARNING
API_KEY_REQUIRED=true
RATE_LIMIT=100/minute
CORS_ORIGINS=https://yourdomain.com
```

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your demo following the guidelines above
4. Test thoroughly
5. Submit a pull request

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for secure, educational networking demonstrations**
