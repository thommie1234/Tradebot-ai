"""
Task scheduler for plugin execution.
"""
import asyncio
from typing import Callable, Dict, Optional
from datetime import datetime, time as dt_time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .logger import logger
from .errors import ConfigError


class Scheduler:
    """
    Task scheduler wrapper around APScheduler.
    Supports cron, interval, and special market-time triggers.
    """

    def __init__(self):
        """Initialize scheduler."""
        self._scheduler = AsyncIOScheduler()
        self._jobs: Dict[str, str] = {}  # plugin_id -> job_id
        self._market_hours = {
            "open": dt_time(9, 30),  # 9:30 AM ET
            "close": dt_time(16, 0),  # 4:00 PM ET
        }

    async def start(self) -> None:
        """Start scheduler."""
        self._scheduler.start()
        logger.info("Scheduler started")

    async def stop(self) -> None:
        """Stop scheduler."""
        self._scheduler.shutdown()
        logger.info("Scheduler stopped")

    def schedule_plugin(
        self,
        plugin_id: str,
        schedule: str,
        func: Callable,
        *args,
        **kwargs,
    ) -> None:
        """
        Schedule a plugin to run.

        Args:
            plugin_id: Plugin identifier
            schedule: Schedule string (cron, @idle, @open, @close, interval_Xs)
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        # Remove existing job if present
        if plugin_id in self._jobs:
            self.unschedule_plugin(plugin_id)

        # Parse schedule
        trigger = self._parse_schedule(schedule)

        # Add job
        job = self._scheduler.add_job(
            func,
            trigger,
            args=args,
            kwargs=kwargs,
            id=plugin_id,
            name=plugin_id,
            max_instances=1,  # Prevent overlapping runs
            coalesce=True,  # Combine missed runs
        )

        self._jobs[plugin_id] = job.id
        logger.info(f"Scheduled plugin {plugin_id}: {schedule}")

    def unschedule_plugin(self, plugin_id: str) -> None:
        """
        Unschedule a plugin.

        Args:
            plugin_id: Plugin identifier
        """
        if plugin_id in self._jobs:
            job_id = self._jobs.pop(plugin_id)
            self._scheduler.remove_job(job_id)
            logger.info(f"Unscheduled plugin {plugin_id}")

    def _parse_schedule(self, schedule: str):
        """
        Parse schedule string into APScheduler trigger.

        Args:
            schedule: Schedule string

        Returns:
            APScheduler trigger object
        """
        # Special triggers
        if schedule == "@idle":
            # Run every 5 minutes during off-market hours
            return CronTrigger(minute="*/5")

        elif schedule == "@open":
            # Run at market open (9:30 AM ET on weekdays)
            return CronTrigger(
                day_of_week="mon-fri",
                hour=9,
                minute=30,
                timezone="America/New_York",
            )

        elif schedule == "@close":
            # Run at market close (4:00 PM ET on weekdays)
            return CronTrigger(
                day_of_week="mon-fri",
                hour=16,
                minute=0,
                timezone="America/New_York",
            )

        elif schedule.startswith("interval_"):
            # Interval trigger: interval_30s, interval_5m, interval_1h
            value, unit = schedule[9:-1], schedule[-1]
            value = int(value)

            if unit == "s":
                return IntervalTrigger(seconds=value)
            elif unit == "m":
                return IntervalTrigger(minutes=value)
            elif unit == "h":
                return IntervalTrigger(hours=value)
            else:
                raise ConfigError(f"Invalid interval unit: {unit}")

        else:
            # Cron expression
            try:
                return CronTrigger.from_crontab(schedule)
            except Exception as e:
                raise ConfigError(f"Invalid cron expression '{schedule}': {e}")

    def get_next_run_time(self, plugin_id: str) -> Optional[datetime]:
        """
        Get next run time for a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Next run time or None
        """
        if plugin_id in self._jobs:
            job = self._scheduler.get_job(self._jobs[plugin_id])
            return job.next_run_time if job else None
        return None

    def get_scheduled_plugins(self) -> Dict[str, datetime]:
        """
        Get all scheduled plugins and their next run times.

        Returns:
            Dictionary of plugin_id -> next_run_time
        """
        result = {}
        for plugin_id, job_id in self._jobs.items():
            job = self._scheduler.get_job(job_id)
            if job:
                result[plugin_id] = job.next_run_time
        return result

    def pause_plugin(self, plugin_id: str) -> None:
        """Pause a plugin's schedule."""
        if plugin_id in self._jobs:
            self._scheduler.pause_job(self._jobs[plugin_id])
            logger.info(f"Paused plugin {plugin_id}")

    def resume_plugin(self, plugin_id: str) -> None:
        """Resume a plugin's schedule."""
        if plugin_id in self._jobs:
            self._scheduler.resume_job(self._jobs[plugin_id])
            logger.info(f"Resumed plugin {plugin_id}")
