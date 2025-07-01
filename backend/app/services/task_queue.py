"""
Task Queue Service using Celery for Background Operations

This service provides task queue functionality for long-running operations
that should not block the main Flask application thread.
"""

import os
import logging
from celery import Celery

logger = logging.getLogger(__name__)

def make_celery(app):
    """
    Create and configure Celery instance for Flask application.
    
    Args:
        app: Flask application instance
        
    Returns:
        Configured Celery instance
    """
    # Default Celery configuration
    celery_config = {
        'broker_url': os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        'result_backend': os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'UTC',
        'enable_utc': True,
        'task_track_started': True,
        'task_time_limit': 30 * 60,  # 30 minutes
        'task_soft_time_limit': 25 * 60,  # 25 minutes
        'worker_prefetch_multiplier': 1,
        'task_acks_late': True,
        'worker_max_tasks_per_child': 50,
    }
    
    # Create Celery instance
    celery = Celery(
        app.import_name,
        broker=celery_config['broker_url'],
        backend=celery_config['result_backend']
    )
    
    # Update Celery configuration
    celery.conf.update(celery_config)
    
    # Update task base classes for Flask context
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    logger.info("Celery configured successfully")
    return celery

def get_task_status(task_id, celery_app):
    """
    Get the status of a Celery task.
    
    Args:
        task_id: ID of the task to check
        celery_app: Celery application instance
        
    Returns:
        Dict with task status information
    """
    try:
        from celery.result import AsyncResult
        result = AsyncResult(task_id, app=celery_app)
        
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None,
            'traceback': result.traceback if result.failed() else None,
            'info': result.info
        }
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return {
            'task_id': task_id,
            'status': 'ERROR',
            'error': str(e)
        }

def revoke_task(task_id, celery_app, terminate=False):
    """
    Revoke a Celery task.
    
    Args:
        task_id: ID of the task to revoke
        celery_app: Celery application instance
        terminate: Whether to terminate the task if it's running
        
    Returns:
        Dict with revocation status
    """
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        return {
            'task_id': task_id,
            'status': 'revoked',
            'terminated': terminate
        }
    except Exception as e:
        logger.error(f"Error revoking task: {str(e)}")
        return {
            'task_id': task_id,
            'status': 'error',
            'error': str(e)
        }

def get_active_tasks(celery_app):
    """
    Get list of active tasks.
    
    Args:
        celery_app: Celery application instance
        
    Returns:
        List of active task information
    """
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if active_tasks:
            # Flatten the dictionary of worker -> tasks to a simple list
            all_tasks = []
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    task['worker'] = worker
                    all_tasks.append(task)
            return all_tasks
        return []
    except Exception as e:
        logger.error(f"Error getting active tasks: {str(e)}")
        return []

def get_worker_stats(celery_app):
    """
    Get Celery worker statistics.
    
    Args:
        celery_app: Celery application instance
        
    Returns:
        Dict with worker statistics
    """
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        return {
            'workers': stats or {},
            'registered_tasks': inspect.registered() or {},
            'reserved_tasks': inspect.reserved() or {},
            'scheduled_tasks': inspect.scheduled() or {}
        }
    except Exception as e:
        logger.error(f"Error getting worker stats: {str(e)}")
        return {
            'error': str(e),
            'workers': {},
            'registered_tasks': {},
            'reserved_tasks': {},
            'scheduled_tasks': {}
        } 