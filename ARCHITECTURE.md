# Architecture: Production-Grade Networking Demo Platform

## Overview

This platform transforms educational networking scripts into a secure, production-ready web application that allows users to run predefined networking demonstrations through a web UI.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│                     (React/Next.js UI)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │   API Routes │  │  Validation  │  │  Demo Registry   │     │
│  │   /api/...   │─▶│  (Pydantic)  │─▶│  (Recipes)       │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
│         │                                      │                │
│         │                                      │                │
│         ▼                                      ▼                │
│  ┌──────────────────────────────────────────────────────┐      │
│  │           Job Queue (Redis + RQ/Celery)              │      │
│  │         - Async job submission                        │      │
│  │         - Job status tracking                         │      │
│  │         - Result storage                              │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Job Messages
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WORKER SERVICE                             │
│  ┌──────────────────────────────────────────────────────┐      │
│  │         Job Processor (Python Worker)                 │      │
│  │   - Receives jobs from queue                          │      │
│  │   - Spawns isolated Docker containers                 │      │
│  │   - Executes demo with validated parameters           │      │
│  │   - Captures structured output (JSON)                 │      │
│  │   - Returns results to queue                          │      │
│  └─────────────┬────────────────────────────────────────┘      │
└────────────────┼───────────────────────────────────────────────┘
                 │
                 │ Docker API
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              EXECUTION CONTAINERS (Sandboxed)                   │
│  ┌────────────────────────────────────────────────────┐        │
│  │  Demo Execution Environment                         │        │
│  │  - Non-root user (uid 1000)                         │        │
│  │  - CPU limit: 1 core                                │        │
│  │  - Memory limit: 512MB                              │        │
│  │  - Execution timeout: 30s                           │        │
│  │  - Read-only filesystem (except /tmp)               │        │
│  │  - Network: disabled (or restricted)                │        │
│  │  - No privilege escalation                          │        │
│  └────────────────────────────────────────────────────┘        │
│         ▼ Structured JSON Output                                │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React/Next.js)

**Responsibilities:**
- Display available demo recipes
- Provide parameter input forms with client-side validation
- Submit jobs to backend API
- Poll for job status and results
- Display structured output (JSON visualization)

**Technology Stack:**
- React or Next.js
- TypeScript (optional but recommended)
- Tailwind CSS or Material-UI for styling
- Axios or Fetch API for HTTP requests

### 2. Backend API (FastAPI)

**Responsibilities:**
- Expose REST API endpoints
- Validate incoming requests using Pydantic schemas
- Submit jobs to queue
- Query job status
- Return results

**Key Endpoints:**
```
GET  /api/demos              - List all available demo recipes
GET  /api/demos/{demo_id}    - Get demo details and parameter schema
POST /api/jobs               - Submit a new demo execution job
GET  /api/jobs/{job_id}      - Get job status and results
GET  /api/health             - Health check endpoint
```

**Technology Stack:**
- FastAPI
- Pydantic for validation
- Redis client for job queue interaction
- Structured logging (python-json-logger)

### 3. Job Queue (Redis + RQ/Celery)

**Responsibilities:**
- Queue demo execution jobs
- Track job status (pending, running, completed, failed)
- Store results temporarily
- Handle job timeouts and retries

**Configuration:**
- Redis as message broker and result backend
- Job TTL: 1 hour
- Max retries: 0 (fail fast)
- Timeout: 60 seconds

### 4. Worker Service

**Responsibilities:**
- Poll queue for pending jobs
- Validate job parameters (double-check)
- Spawn Docker containers for execution
- Monitor execution and enforce timeouts
- Capture output and structure as JSON
- Update job status and store results

**Security Measures:**
- No dynamic code execution
- Only registered demo recipes allowed
- Container isolation enforced
- Resource limits applied
- Network restrictions

### 5. Execution Containers

**Responsibilities:**
- Provide isolated execution environment
- Run demo code with validated parameters
- Enforce security constraints

**Security Configuration:**
```dockerfile
# Non-root user
USER demouser:demouser

# Resource limits (in docker-compose)
cpus: '1.0'
mem_limit: 512m
pids_limit: 100

# Security options
read_only: true
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
network_mode: none  # or bridge with restrictions
```

## Data Flow

### Demo Execution Flow

1. **User Interaction:**
   - User selects demo from UI
   - UI fetches parameter schema
   - User fills in parameters
   - UI validates and submits job

2. **API Processing:**
   - FastAPI receives request
   - Validates demo_id exists
   - Validates parameters against schema
   - Generates unique job_id
   - Submits job to Redis queue
   - Returns job_id to client

3. **Worker Processing:**
   - Worker picks up job from queue
   - Retrieves demo recipe
   - Spawns Docker container with:
     - Demo code
     - Validated parameters
     - Security constraints
   - Monitors execution
   - Captures structured output
   - Updates job status in Redis

4. **Result Retrieval:**
   - Client polls `/api/jobs/{job_id}`
   - API queries Redis for status
   - Returns current status and results
   - Results include:
     - Status (pending/running/completed/failed)
     - Output (JSON)
     - Execution time
     - Error messages (if failed)

## Security Model

### Defense in Depth

**Layer 1: Input Validation**
- Strict Pydantic schemas for all parameters
- Whitelist approach: only known fields accepted
- Type checking, range validation, format validation
- No user-supplied code or commands

**Layer 2: Demo Registry**
- Only predefined demos can be executed
- Demo code is static, reviewed, and versioned
- No dynamic imports or eval()
- Parameters are data only, never code

**Layer 3: Container Isolation**
- Each execution in separate container
- Non-root user (UID 1000)
- Read-only root filesystem
- Limited /tmp for temporary files
- No privilege escalation
- Dropped capabilities

**Layer 4: Resource Limits**
- CPU: max 1 core
- Memory: max 512MB
- Process count: max 100
- Execution timeout: 30-60s
- Network: disabled unless explicitly required

**Layer 5: Monitoring & Logging**
- All requests logged
- Job execution logged
- Failed attempts logged
- Resource usage tracked
- Alerts on anomalies

### Threat Mitigation

| Threat | Mitigation |
|--------|-----------|
| Arbitrary code execution | Only predefined demos; no eval/exec |
| Resource exhaustion | Container CPU/memory/time limits |
| Privilege escalation | Non-root user, dropped capabilities |
| Network attacks | Network disabled in containers |
| Data exfiltration | Read-only filesystem, no internet |
| DoS attacks | Rate limiting, job queue limits |
| Injection attacks | Strict input validation with Pydantic |

## Demo Recipe Structure

### Recipe Definition

Each demo is registered with:

```python
DemoRecipe(
    id="tcp-handshake",
    name="TCP 3-Way Handshake",
    description="Demonstrates TCP connection establishment",
    category="layer4",
    parameters_schema=TCPHandshakeParams,
    max_runtime=30,
    requires_network=False,
    function=execute_tcp_handshake,
)
```

### Parameter Schema Example

```python
class TCPHandshakeParams(BaseModel):
    target_ip: str = Field(
        ...,
        regex=r"^(\d{1,3}\.){3}\d{1,3}$",
        description="Target IP address"
    )
    target_port: int = Field(
        ...,
        ge=1,
        le=65535,
        description="Target port number"
    )
    timeout: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Timeout in seconds"
    )
```

### Demo Function Contract

```python
def execute_tcp_handshake(params: TCPHandshakeParams) -> dict:
    """
    Execute TCP handshake demo.
    
    Args:
        params: Validated parameters
        
    Returns:
        Structured JSON output with:
        - success: bool
        - data: dict (demo-specific results)
        - error: str (if failed)
        - metadata: dict (execution time, etc.)
    """
    # Pure function - no side effects except network I/O
    # Returns structured JSON only
    pass
```

## Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | React/Next.js | Latest stable |
| Backend API | FastAPI | 0.100+ |
| Validation | Pydantic | 2.0+ |
| Queue | Redis | 7.0+ |
| Worker | RQ or Celery | Latest |
| Container | Docker | 20.10+ |
| Orchestration | Docker Compose | 2.0+ |
| Python | CPython | 3.11+ |

## Deployment Considerations

### Development Environment
```bash
docker-compose up
# Starts: Redis, API, Worker, Frontend
# Available at: http://localhost:3000
```

### Production Deployment
- Use Kubernetes for orchestration
- Redis cluster for high availability
- Multiple worker replicas for scalability
- HTTPS/TLS termination at load balancer
- Rate limiting and authentication
- Monitoring with Prometheus/Grafana
- Centralized logging with ELK stack

## Extending the System

### Adding a New Demo

1. **Create Demo Function:**
   ```python
   # demos/layer4/my_new_demo.py
   def execute_my_demo(params: MyDemoParams) -> dict:
       # Implementation
       return {"success": True, "data": {...}}
   ```

2. **Define Parameter Schema:**
   ```python
   # schemas/demos.py
   class MyDemoParams(BaseModel):
       param1: str
       param2: int
   ```

3. **Register Demo:**
   ```python
   # demos/registry.py
   register_demo(DemoRecipe(
       id="my-new-demo",
       name="My New Demo",
       parameters_schema=MyDemoParams,
       function=execute_my_demo,
   ))
   ```

4. **Update Documentation:**
   - Add to README
   - Document parameters
   - Add usage examples

No other changes needed - the system automatically:
- Exposes the demo via API
- Validates parameters
- Executes in isolated container
- Returns structured results

## Monitoring & Observability

- **Health Checks:** API and worker health endpoints
- **Metrics:** Job success/failure rates, execution times, resource usage
- **Logging:** Structured JSON logs with correlation IDs
- **Tracing:** Request tracing through the system
- **Alerts:** Failed jobs, resource exhaustion, anomalies

## Future Enhancements

- User authentication and authorization
- Rate limiting per user
- Job history and audit trail
- Demo output visualization (graphs, charts)
- Real-time execution logs streaming
- Demo chaining and workflows
- Saved parameter presets
- Scheduled demo execution
- Integration with CI/CD pipelines
