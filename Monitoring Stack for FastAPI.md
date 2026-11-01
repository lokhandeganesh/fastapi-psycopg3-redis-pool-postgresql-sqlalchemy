https://medium.com/@diwasb54/building-a-production-ready-monitoring-stack-for-fastapi-applications-a-complete-guide-with-bce2af74d258

### Building a Production-Ready Monitoring Stack for FastAPI Applications: A Complete Guide with Prometheus and Grafana

#### The Challenge: Why Monitoring Matters More Than You Think

Picture this: It’s 2 AM, and your FastAPI application is experiencing mysterious slowdowns. Users are complaining, but you have no visibility into what’s happening. Is it a database bottleneck? Memory leak? Sudden traffic spike? Without proper monitoring, you’re flying blind.

In today’s microservices-driven world, observability isn’t optional - it’s essential. Whether you’re running a simple API or a complex distributed system, understanding your application’s behavior in real-time can mean the difference between a minor hiccup and a full-scale outage.

This guide will walk you through building a production-ready monitoring stack that gives you deep insights into your FastAPI application’s performance, complete with beautiful dashboards and actionable alerts.

#### What We’re Building: The Complete Picture

By the end of this article, you’ll have:

* A FastAPI application instrumented with custom metrics
* Prometheus collecting and storing metrics data
* Grafana providing stunning visualizations and dashboards
* Docker Compose orchestrating everything seamlessly
* Real-world examples you can adapt to your own applications

Let’s dive in!

**Part 1: Setting Up Your FastAPI Application with Metrics**

The Foundation: Creating Our Sample Application
First, let’s create a FastAPI application that simulates real-world scenarios.
We’ll include endpoints that demonstrate different performance characteristics - fast responses, slow operations, and error conditions.

Project Structure:

```yaml
fastapi-monitoring/
├── app/
│   ├── main.py                    # Our instrumented FastAPI app
│   ├── requirements.txt           # Dependencies
│   └── Dockerfile                 # Container definition
├── prometheus/
│   └── prometheus.yml             # Metrics collection config
├── grafana/
│   ├── provisioning/              # Auto-configuration
│   └── dashboards/                # Pre-built dashboards
└── docker-compose.yml             # Orchestration magic
```

**app/main.py** - The Heart of Our Monitoring Setup

```python
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
import random
import psutil
import asyncio

app = FastAPI(title="FastAPI Monitoring Demo", version="1.0.0")

# Custom Prometheus Metrics - The Foundation of Good Monitoring
REQUEST_COUNT = Counter(
    'fastapi_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'fastapi_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)
ACTIVE_REQUESTS = Gauge(
    'fastapi_active_requests',
    'Active HTTP requests currently being processed'
)
CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)
MEMORY_USAGE = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage'
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    """
    Automatic metrics collection middleware
    This captures every request without modifying your business logic
    """
    start_time = time.time()
    ACTIVE_REQUESTS.inc()

    response = await call_next(request)

    # Record comprehensive metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)

    ACTIVE_REQUESTS.dec()
    return response

@app.on_event("startup")
async def startup_event():
    """Start background system monitoring"""
    asyncio.create_task(update_system_metrics())

async def update_system_metrics():
    """
    Continuous system metrics collection
    Updates every 5 seconds with current system state
    """
    while True:
        CPU_USAGE.set(psutil.cpu_percent())
        MEMORY_USAGE.set(psutil.virtual_memory().percent)
        await asyncio.sleep(5)

# API Endpoints - Real-world scenarios for testing
@app.get("/")
async def root():
    """Simple health endpoint"""
    return {"message": "FastAPI Monitoring Demo", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check with timestamp"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    """
    User endpoint with variable response time
    Simulates database calls with realistic latency
    """
    # Simulate realistic processing time
    await asyncio.sleep(random.uniform(0.1, 0.5))

    # Simulate not found scenarios
    if user_id == 404:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }

@app.get("/api/slow")
async def slow_endpoint():
    """
    Intentionally slow endpoint
    Perfect for testing high-percentile response times
    """
    delay = random.uniform(1, 3)
    await asyncio.sleep(delay)
    return {
        "message": "This endpoint simulates slow operations",
        "actual_delay": f"{delay:.2f} seconds"
    }

@app.get("/api/error")
async def error_endpoint():
    """
    Endpoint that randomly fails
    Great for testing error rate monitoring
    """
    if random.random() < 0.3:  # 30% error rate
        raise HTTPException(status_code=500, detail="Simulated server error")

    if random.random() < 0.1:  # 10% client error rate
        raise HTTPException(status_code=400, detail="Simulated client error")

    return {"message": "Success!", "random_value": random.randint(1, 100)}

@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    This is where Prometheus scrapes our metrics
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

```

**app/requirements.txt**

```bash
fastapi==0.104.1
uvicorn[standard]==0.24.0
prometheus-client==0.19.0
psutil==5.9.6
```

**app/Dockerfile**

```bash
FROM python:3.11-slim

# Optimized for development and production
WORKDIR /app

# Install system dependencies for psutil
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
