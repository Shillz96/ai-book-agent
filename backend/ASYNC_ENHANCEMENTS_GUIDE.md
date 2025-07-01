# Asynchronous Operations and Task Queue Enhancements

## Overview

The AI Book Marketing Agent backend has been enhanced with robust asynchronous operations and task queue management to prevent blocking operations and improve scalability. This guide explains the new features and how to use them.

## Key Improvements

### 1. Non-Blocking Operations
- **Problem Solved**: Previously, `asyncio.run()` calls in Flask routes blocked the entire worker process
- **Solution**: Implemented thread pool executor and Celery task queues for background processing
- **Benefits**: Better responsiveness, higher concurrency, improved user experience

### 2. Task Queue System
- **Dual Approach**: Celery (primary) with thread pool fallback
- **Background Processing**: Long-running operations execute without blocking API responses
- **Task Monitoring**: Comprehensive task status tracking and management

### 3. Enhanced Error Handling
- **Timeouts**: Configurable timeouts for all async operations
- **Graceful Degradation**: Automatic fallback to simpler implementations
- **Resource Cleanup**: Proper cleanup on application shutdown

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flask App     │    │   Task Queue     │    │   Background    │
│                 │    │                  │    │   Workers       │
│ • API Endpoints │────│ • Celery (Redis) │────│ • Content Gen   │
│ • Thread Pool   │    │ • Thread Pool    │    │ • Analytics     │
│ • Task Tracking │    │ • Task Status    │    │ • Reports       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Installation and Setup

### 1. Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install enhanced requirements
pip install -r requirements.txt
```

### 2. Redis Setup (for Celery)

**Option A: Local Redis**
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Start Redis
redis-server
```

**Option B: Docker Redis**
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 3. Environment Configuration

Add to your `.env` file:
```env
# Task Queue Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_LOG_LEVEL=info
CELERY_CONCURRENCY=4
```

### 4. Start the Services

**Terminal 1: Flask Application**
```bash
cd backend
python main.py
```

**Terminal 2: Celery Worker (if using Celery)**
```bash
cd backend
python start_celery.py
```

## API Usage Examples

### 1. Asynchronous Content Generation

**For Large Batches (Automatic Background Processing)**
```python
import requests

# Generate 10+ posts automatically uses background processing
response = requests.post("http://localhost:5000/api/generate-posts", json={
    "user_id": "user123",
    "platforms": ["twitter", "facebook", "instagram"],
    "count_per_platform": 5,  # 15 total posts - triggers async
    "async": False  # Can force async even for smaller batches
})

# Response for background task
{
    "status": "content_generation_queued",
    "task_id": "abc123",
    "timestamp": "2024-01-15T10:00:00Z",
    "message": "Generating 15 posts in background. Check task status for results."
}
```

**For Small Batches (Synchronous)**
```python
# Small batches processed immediately
response = requests.post("http://localhost:5000/api/generate-posts", json={
    "user_id": "user123",
    "platforms": ["twitter"],
    "count_per_platform": 2  # 2 total posts - processed immediately
})

# Immediate response with posts
{
    "posts_generated": 2,
    "posts": [...],
    "timestamp": "2024-01-15T10:00:00Z"
}
```

### 2. Background Task Management

**Check Task Status**
```python
response = requests.get(f"http://localhost:5000/api/task-status/{task_id}")

# Response
{
    "task_id": "abc123",
    "status": "SUCCESS",  # PENDING, SUCCESS, FAILURE
    "result": {
        "posts": [...],
        "count": 15
    },
    "started_at": "2024-01-15T10:00:00Z"
}
```

**Get Active Tasks**
```python
response = requests.get("http://localhost:5000/api/tasks/active")

# Response
{
    "active_tasks": [
        {
            "task_id": "abc123",
            "type": "celery",
            "name": "content_generation_batch_task",
            "worker": "worker1@hostname"
        }
    ],
    "count": 1
}
```

**Cancel/Revoke Task**
```python
response = requests.post(f"http://localhost:5000/api/tasks/revoke/{task_id}", json={
    "terminate": true  # Force terminate if running
})
```

### 3. Enhanced Autonomous Operations

**Start Autonomous Operations (Non-blocking)**
```python
response = requests.post("http://localhost:5000/api/autonomous/start")

# Returns immediately, operation runs in background
{
    "status": "autonomous_operation_started",
    "timestamp": "2024-01-15T10:00:00Z"
}
```

**Daily Operations (Background Task)**
```python
response = requests.post("http://localhost:5000/api/autonomous/execute-daily")

# Returns task ID for monitoring
{
    "status": "daily_operations_queued",
    "task_id": "daily_123",
    "message": "Daily operations started in background."
}
```

## Task Types and Timeouts

| Task Type | Default Timeout | Description |
|-----------|----------------|-------------|
| Content Generation | 300s (5 min) | Batch post generation |
| Weekly Reports | 600s (10 min) | Comprehensive analytics |
| Daily Operations | 300s (5 min) | Autonomous daily tasks |
| Post Approval | 30s | Schedule and approve posts |
| Status Checks | 15s | Quick status queries |

## Monitoring and Debugging

### 1. Health Check

```python
response = requests.get("http://localhost:5000/api/health")

# Enhanced health check response
{
    "status": "healthy",
    "services": {...},
    "task_queue_status": {
        "type": "celery",  # or "thread_pool"
        "active_tasks": 3
    },
    "autonomous_status": {...}
}
```

### 2. Task Queue Statistics

```python
response = requests.get("http://localhost:5000/api/tasks/stats")

# Detailed statistics
{
    "thread_pool": {
        "max_workers": 4,
        "active_tasks": 2,
        "total_tracked": 5
    },
    "celery": {
        "workers": {...},
        "registered_tasks": {...}
    }
}
```

### 3. Application Logs

The enhanced logging provides detailed information about:
- Task creation and completion
- Timeout events
- Resource cleanup
- Background operation status

```
2024-01-15 10:00:00 - INFO - Content generation queued: task_abc123
2024-01-15 10:00:30 - INFO - Task abc123 completed successfully
2024-01-15 10:01:00 - WARNING - Operation timeout after 30s: get_autonomous_status
```

## Error Handling

### Common Issues and Solutions

**1. Redis Connection Failed**
```
Error: Celery initialization failed: [Errno 111] Connection refused
Solution: Ensure Redis is running on localhost:6379
```

**2. Task Timeout**
```
Error: Operation timed out after 30 seconds
Solution: Increase timeout or check task complexity
```

**3. Background Task Failed**
```
Task Status: FAILURE
Solution: Check task result for detailed error message
```

## Production Deployment

### 1. Redis Configuration

For production, use a dedicated Redis instance with:
```env
CELERY_BROKER_URL=redis://your-redis-host:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-host:6379/0
```

### 2. Multiple Workers

Scale Celery workers based on load:
```bash
# Start multiple workers
celery -A main.celery_app worker --concurrency=8 --hostname=worker1@%h
celery -A main.celery_app worker --concurrency=8 --hostname=worker2@%h
```

### 3. Monitoring

Use Celery monitoring tools:
```bash
# Flower (Web-based monitoring)
pip install flower
celery -A main.celery_app flower

# Command-line monitoring
celery -A main.celery_app inspect active
celery -A main.celery_app inspect stats
```

## Performance Benefits

### Before Enhancement
- **Blocking Operations**: Single request could block entire worker
- **Poor Concurrency**: Limited to sequential processing
- **User Experience**: Long waits for complex operations
- **Resource Usage**: Inefficient thread utilization

### After Enhancement
- **Non-Blocking**: All long operations run in background
- **High Concurrency**: Multiple requests processed simultaneously
- **Better UX**: Immediate responses with status tracking
- **Efficient Resources**: Optimal thread and worker utilization

## Best Practices

1. **Use Async for Large Operations**: Enable async for batch sizes > 5
2. **Monitor Task Status**: Always provide users with task progress
3. **Set Appropriate Timeouts**: Balance responsiveness vs completion
4. **Handle Failures Gracefully**: Implement retry logic where appropriate
5. **Clean Up Resources**: Ensure proper cleanup on shutdown

## Troubleshooting

### Debug Mode
```python
# Enable detailed logging
CELERY_LOG_LEVEL=debug
```

### Manual Task Inspection
```python
from main import celery_app
from celery.result import AsyncResult

result = AsyncResult('task-id', app=celery_app)
print(f"Status: {result.status}")
print(f"Result: {result.result}")
print(f"Traceback: {result.traceback}")
```

### Health Checks
- **Flask Health**: `GET /api/health`
- **Task Queue Stats**: `GET /api/tasks/stats`
- **Active Tasks**: `GET /api/tasks/active`

This enhanced system provides a robust foundation for scalable, production-ready deployment while maintaining backward compatibility with existing functionality. 