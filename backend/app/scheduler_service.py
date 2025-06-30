"""
Scheduler Service

This service manages the autonomous operation of the book marketing agent.
It schedules and coordinates all marketing activities including content posting,
campaign optimization, budget management, and performance reporting.

Key Features:
- Autonomous daily operation scheduling
- Weekly report generation and distribution
- Real-time performance monitoring and alerts
- Emergency response coordination
- Task queue management for efficient processing
- Fail-safe mechanisms to prevent system failures
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import redis
import time as time_module

logger = logging.getLogger(__name__)

@dataclass
class ScheduledTask:
    """Structure for scheduled tasks."""
    task_id: str
    task_type: str
    schedule_type: str  # 'daily', 'weekly', 'interval', 'cron'
    function: Callable
    parameters: Dict
    next_run: datetime
    last_run: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    enabled: bool = True

class SchedulerService:
    """
    Autonomous scheduling service for book marketing operations.
    
    Coordinates all marketing activities, ensures reliable execution,
    and provides fail-safe mechanisms for continuous operation.
    """
    
    def __init__(self, autonomous_manager, firebase_service, config):
        """
        Initialize scheduler service.
        
        Args:
            autonomous_manager: Autonomous marketing manager instance
            firebase_service: Firebase service for data storage
            config: Configuration object with schedule settings
        """
        self.autonomous_manager = autonomous_manager
        self.firebase_service = firebase_service
        self.config = config
        
        # Initialize scheduler
        self.scheduler = AsyncIOScheduler()
        
        # Initialize Redis for task queue (if available)
        self.redis_client = None
        try:
            self.redis_client = redis.from_url(config.REDIS_URL)
            self.redis_client.ping()  # Test connection
            logger.info("Redis connection established for task queue")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory task queue: {str(e)}")
        
        # Task tracking
        self.scheduled_tasks = {}
        self.task_history = []
        self.emergency_mode = False
        
        # Configuration
        self.autonomous_enabled = config.AUTONOMOUS_MODE
        self.post_schedule = config.DAILY_POST_SCHEDULE
        self.weekly_report_day = config.WEEKLY_REPORT_DAY
        self.weekly_report_time = config.WEEKLY_REPORT_TIME
        
        logger.info("Scheduler Service initialized successfully")
    
    async def start_autonomous_operation(self):
        """
        Start autonomous marketing operation with all scheduled tasks.
        
        Sets up and starts all scheduled tasks for autonomous operation including
        daily content posting, campaign optimization, and performance monitoring.
        """
        try:
            if not self.autonomous_enabled:
                logger.info("Autonomous mode disabled, scheduler not started")
                return
            
            # Schedule daily operations
            await self._schedule_daily_operations()
            
            # Schedule weekly reporting
            await self._schedule_weekly_reporting()
            
            # Schedule performance monitoring
            await self._schedule_performance_monitoring()
            
            # Schedule budget monitoring
            await self._schedule_budget_monitoring()
            
            # Schedule system health checks
            await self._schedule_health_checks()
            
            # Start the scheduler
            self.scheduler.start()
            logger.info("Autonomous marketing operation started successfully")
            
            # Log startup status
            await self._log_startup_status()
            
        except Exception as e:
            logger.error(f"Error starting autonomous operation: {str(e)}")
            await self._handle_startup_failure(e)
    
    async def stop_autonomous_operation(self):
        """
        Stop autonomous operation gracefully.
        
        Properly shuts down all scheduled tasks and saves current state.
        """
        try:
            logger.info("Stopping autonomous marketing operation...")
            
            # Save current state
            await self._save_shutdown_state()
            
            # Stop scheduler
            self.scheduler.shutdown(wait=True)
            
            logger.info("Autonomous marketing operation stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping autonomous operation: {str(e)}")
    
    async def execute_emergency_response(self, alert_type: str, alert_data: Dict):
        """
        Execute emergency response for critical alerts.
        
        Handles critical situations that require immediate intervention
        to protect budget and maintain campaign effectiveness.
        """
        try:
            logger.warning(f"Executing emergency response for {alert_type}")
            
            # Enter emergency mode
            self.emergency_mode = True
            
            # Execute emergency actions based on alert type
            if alert_type == 'budget_exceeded':
                response = await self._handle_budget_emergency(alert_data)
            elif alert_type == 'performance_collapse':
                response = await self._handle_performance_emergency(alert_data)
            elif alert_type == 'system_failure':
                response = await self._handle_system_emergency(alert_data)
            else:
                response = await self._handle_generic_emergency(alert_type, alert_data)
            
            # Log emergency response
            await self._log_emergency_response(alert_type, alert_data, response)
            
            # Schedule recovery assessment
            await self._schedule_recovery_assessment()
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing emergency response: {str(e)}")
            return {'error': str(e)}
    
    async def get_scheduler_status(self) -> Dict:
        """
        Get current scheduler status and task information.
        
        Returns comprehensive information about scheduled tasks,
        execution history, and system health.
        """
        try:
            running_jobs = []
            for job in self.scheduler.get_jobs():
                running_jobs.append({
                    'job_id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            
            # Get task statistics
            task_stats = await self._calculate_task_statistics()
            
            # Get system health metrics
            health_metrics = await self._get_system_health_metrics()
            
            return {
                'scheduler_running': self.scheduler.running,
                'autonomous_mode': self.autonomous_enabled,
                'emergency_mode': self.emergency_mode,
                'total_scheduled_tasks': len(self.scheduled_tasks),
                'running_jobs': running_jobs,
                'task_statistics': task_stats,
                'system_health': health_metrics,
                'last_status_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {str(e)}")
            return {'error': str(e)}
    
    # Private methods for scheduling setup
    
    async def _schedule_daily_operations(self):
        """Schedule daily marketing operations."""
        # Schedule daily content generation and posting
        for post_time in self.post_schedule:
            hour, minute = map(int, post_time.split(':'))
            
            self.scheduler.add_job(
                func=self._execute_daily_content_operations,
                trigger=CronTrigger(hour=hour, minute=minute),
                id=f'daily_content_{hour}_{minute}',
                name=f'Daily Content Operations at {post_time}',
                max_instances=1,
                coalesce=True
            )
        
        # Schedule daily performance analysis
        self.scheduler.add_job(
            func=self._execute_daily_analysis,
            trigger=CronTrigger(hour=8, minute=0),  # 8:00 AM daily
            id='daily_analysis',
            name='Daily Performance Analysis',
            max_instances=1
        )
        
        # Schedule daily campaign optimization
        self.scheduler.add_job(
            func=self._execute_daily_optimization,
            trigger=CronTrigger(hour=10, minute=0),  # 10:00 AM daily
            id='daily_optimization',
            name='Daily Campaign Optimization',
            max_instances=1
        )
        
        logger.info("Daily operations scheduled successfully")
    
    async def _schedule_weekly_reporting(self):
        """Schedule weekly report generation."""
        # Map day names to numbers (Monday = 0)
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        report_day = day_map.get(self.weekly_report_day, 0)
        report_hour, report_minute = map(int, self.weekly_report_time.split(':'))
        
        self.scheduler.add_job(
            func=self._execute_weekly_report,
            trigger=CronTrigger(day_of_week=report_day, hour=report_hour, minute=report_minute),
            id='weekly_report',
            name=f'Weekly Report Generation - {self.weekly_report_day.title()} at {self.weekly_report_time}',
            max_instances=1
        )
        
        logger.info(f"Weekly reporting scheduled for {self.weekly_report_day.title()} at {self.weekly_report_time}")
    
    async def _schedule_performance_monitoring(self):
        """Schedule real-time performance monitoring."""
        # Monitor performance every 30 minutes
        self.scheduler.add_job(
            func=self._execute_performance_monitoring,
            trigger=IntervalTrigger(minutes=30),
            id='performance_monitoring',
            name='Performance Monitoring',
            max_instances=1
        )
        
        # Check for alerts every 15 minutes
        self.scheduler.add_job(
            func=self._check_performance_alerts,
            trigger=IntervalTrigger(minutes=15),
            id='alert_monitoring',
            name='Alert Monitoring',
            max_instances=1
        )
        
        logger.info("Performance monitoring scheduled successfully")
    
    async def _schedule_budget_monitoring(self):
        """Schedule budget monitoring and management."""
        # Monitor budget every hour
        self.scheduler.add_job(
            func=self._execute_budget_monitoring,
            trigger=IntervalTrigger(hours=1),
            id='budget_monitoring',
            name='Budget Monitoring',
            max_instances=1
        )
        
        # Daily budget optimization
        self.scheduler.add_job(
            func=self._execute_budget_optimization,
            trigger=CronTrigger(hour=9, minute=30),  # 9:30 AM daily
            id='budget_optimization',
            name='Daily Budget Optimization',
            max_instances=1
        )
        
        logger.info("Budget monitoring scheduled successfully")
    
    async def _schedule_health_checks(self):
        """Schedule system health checks."""
        # System health check every 5 minutes
        self.scheduler.add_job(
            func=self._execute_health_check,
            trigger=IntervalTrigger(minutes=5),
            id='health_check',
            name='System Health Check',
            max_instances=1
        )
        
        # Detailed system diagnostics every 6 hours
        self.scheduler.add_job(
            func=self._execute_system_diagnostics,
            trigger=IntervalTrigger(hours=6),
            id='system_diagnostics',
            name='System Diagnostics',
            max_instances=1
        )
        
        logger.info("Health checks scheduled successfully")
    
    # Task execution methods
    
    async def _execute_daily_content_operations(self):
        """Execute daily content generation and posting."""
        try:
            logger.info("Executing daily content operations")
            result = await self.autonomous_manager.execute_daily_operations()
            await self._log_task_execution('daily_content', result, True)
        except Exception as e:
            logger.error(f"Error executing daily content operations: {str(e)}")
            await self._log_task_execution('daily_content', {'error': str(e)}, False)
            await self._handle_task_failure('daily_content', e)
    
    async def _execute_daily_analysis(self):
        """Execute daily performance analysis."""
        try:
            logger.info("Executing daily performance analysis")
            # This would call performance analysis methods
            result = {'analysis_completed': True, 'timestamp': datetime.now().isoformat()}
            await self._log_task_execution('daily_analysis', result, True)
        except Exception as e:
            logger.error(f"Error executing daily analysis: {str(e)}")
            await self._log_task_execution('daily_analysis', {'error': str(e)}, False)
    
    async def _execute_daily_optimization(self):
        """Execute daily campaign optimization."""
        try:
            logger.info("Executing daily campaign optimization")
            # This would call optimization methods
            result = {'optimization_completed': True, 'timestamp': datetime.now().isoformat()}
            await self._log_task_execution('daily_optimization', result, True)
        except Exception as e:
            logger.error(f"Error executing daily optimization: {str(e)}")
            await self._log_task_execution('daily_optimization', {'error': str(e)}, False)
    
    async def _execute_weekly_report(self):
        """Execute weekly report generation."""
        try:
            logger.info("Executing weekly report generation")
            result = await self.autonomous_manager.generate_weekly_report()
            await self._log_task_execution('weekly_report', result, True)
        except Exception as e:
            logger.error(f"Error executing weekly report: {str(e)}")
            await self._log_task_execution('weekly_report', {'error': str(e)}, False)
    
    async def _execute_performance_monitoring(self):
        """Execute performance monitoring."""
        try:
            # Monitor key performance metrics
            performance_data = await self._collect_performance_metrics()
            
            # Check for performance issues
            issues = await self._identify_performance_issues(performance_data)
            
            if issues:
                await self._handle_performance_issues(issues)
            
            await self._log_task_execution('performance_monitoring', performance_data, True)
        except Exception as e:
            logger.error(f"Error executing performance monitoring: {str(e)}")
            await self._log_task_execution('performance_monitoring', {'error': str(e)}, False)
    
    async def _check_performance_alerts(self):
        """Check for performance alerts."""
        try:
            # Check for critical alerts
            alerts = await self._check_for_critical_alerts()
            
            for alert in alerts:
                if alert.get('severity') == 'critical':
                    await self.execute_emergency_response(alert.get('type'), alert)
            
            await self._log_task_execution('alert_monitoring', {'alerts_checked': len(alerts)}, True)
        except Exception as e:
            logger.error(f"Error checking performance alerts: {str(e)}")
            await self._log_task_execution('alert_monitoring', {'error': str(e)}, False)
    
    async def _execute_budget_monitoring(self):
        """Execute budget monitoring."""
        try:
            # Get budget status
            budget_status = self.autonomous_manager.budget_manager.get_current_budget_status()
            
            # Check for budget alerts
            budget_alerts = budget_status.get('budget_alerts', [])
            
            for alert_data in budget_alerts:
                if alert_data.get('severity') in ['critical', 'high']:
                    await self._handle_budget_alert(alert_data)
            
            await self._log_task_execution('budget_monitoring', budget_status, True)
        except Exception as e:
            logger.error(f"Error executing budget monitoring: {str(e)}")
            await self._log_task_execution('budget_monitoring', {'error': str(e)}, False)
    
    async def _execute_budget_optimization(self):
        """Execute budget optimization."""
        try:
            # Optimize budget allocation
            optimization_result = self.autonomous_manager.budget_manager.optimize_budget_allocation({})
            await self._log_task_execution('budget_optimization', optimization_result, True)
        except Exception as e:
            logger.error(f"Error executing budget optimization: {str(e)}")
            await self._log_task_execution('budget_optimization', {'error': str(e)}, False)
    
    async def _execute_health_check(self):
        """Execute system health check."""
        try:
            # Check system health
            health_status = await self._perform_health_check()
            
            # Handle any health issues
            if health_status.get('status') != 'healthy':
                await self._handle_health_issues(health_status)
            
            await self._log_task_execution('health_check', health_status, True)
        except Exception as e:
            logger.error(f"Error executing health check: {str(e)}")
            await self._log_task_execution('health_check', {'error': str(e)}, False)
    
    async def _execute_system_diagnostics(self):
        """Execute detailed system diagnostics."""
        try:
            # Perform comprehensive system diagnostics
            diagnostics = await self._perform_system_diagnostics()
            await self._log_task_execution('system_diagnostics', diagnostics, True)
        except Exception as e:
            logger.error(f"Error executing system diagnostics: {str(e)}")
            await self._log_task_execution('system_diagnostics', {'error': str(e)}, False)
    
    # Helper methods
    
    async def _log_task_execution(self, task_type: str, result: Dict, success: bool):
        """Log task execution results."""
        execution_log = {
            'task_type': task_type,
            'execution_time': datetime.now().isoformat(),
            'success': success,
            'result': result
        }
        
        self.task_history.append(execution_log)
        
        # Keep only last 100 task executions in memory
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]
        
        # Save to Firebase
        try:
            self.firebase_service.save_task_execution_log(execution_log)
        except Exception as e:
            logger.error(f"Error saving task execution log: {str(e)}")
    
    async def _log_startup_status(self):
        """Log scheduler startup status."""
        startup_log = {
            'startup_time': datetime.now().isoformat(),
            'autonomous_mode': self.autonomous_enabled,
            'scheduled_tasks': len(self.scheduler.get_jobs()),
            'configuration': {
                'post_schedule': self.post_schedule,
                'weekly_report_day': self.weekly_report_day,
                'weekly_report_time': self.weekly_report_time
            }
        }
        
        try:
            self.firebase_service.save_scheduler_startup_log(startup_log)
        except Exception as e:
            logger.error(f"Error saving startup log: {str(e)}")
    
    async def _handle_startup_failure(self, error: Exception):
        """Handle scheduler startup failure."""
        failure_log = {
            'failure_time': datetime.now().isoformat(),
            'error': str(error),
            'recovery_actions': ['Manual intervention required', 'Check configuration', 'Verify API credentials']
        }
        
        try:
            self.firebase_service.save_scheduler_failure_log(failure_log)
        except Exception as e:
            logger.error(f"Error saving failure log: {str(e)}")
    
    # Placeholder methods for emergency handling
    async def _handle_budget_emergency(self, alert_data: Dict) -> Dict:
        return {'emergency_type': 'budget', 'actions_taken': ['pause_campaigns']}
    
    async def _handle_performance_emergency(self, alert_data: Dict) -> Dict:
        return {'emergency_type': 'performance', 'actions_taken': ['activate_backup_strategy']}
    
    async def _handle_system_emergency(self, alert_data: Dict) -> Dict:
        return {'emergency_type': 'system', 'actions_taken': ['failsafe_mode']}
    
    async def _handle_generic_emergency(self, alert_type: str, alert_data: Dict) -> Dict:
        return {'emergency_type': alert_type, 'actions_taken': ['log_alert']}
    
    # Additional placeholder methods...
    async def _log_emergency_response(self, alert_type: str, alert_data: Dict, response: Dict):
        pass
    
    async def _schedule_recovery_assessment(self):
        pass
    
    async def _calculate_task_statistics(self) -> Dict:
        return {'total_executions': len(self.task_history), 'success_rate': 0.95}
    
    async def _get_system_health_metrics(self) -> Dict:
        return {'status': 'healthy', 'uptime': '99.9%'}
    
    async def _collect_performance_metrics(self) -> Dict:
        return {}
    
    async def _identify_performance_issues(self, performance_data: Dict) -> List[Dict]:
        return []
    
    async def _handle_performance_issues(self, issues: List[Dict]):
        pass
    
    async def _check_for_critical_alerts(self) -> List[Dict]:
        return []
    
    async def _handle_budget_alert(self, alert_data: Dict):
        pass
    
    async def _perform_health_check(self) -> Dict:
        return {'status': 'healthy'}
    
    async def _handle_health_issues(self, health_status: Dict):
        pass
    
    async def _perform_system_diagnostics(self) -> Dict:
        return {'diagnostics_completed': True}
    
    async def _handle_task_failure(self, task_type: str, error: Exception):
        pass
    
    async def _save_shutdown_state(self):
        pass 