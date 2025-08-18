import os
import time
import heapq
import subprocess
from datetime import datetime, timedelta
from calendar import monthrange
from typing import List, Tuple
from pycroner.load import load_config
from pycroner.models import JobInstance, JobSpec
from pycroner.printer import Printer
from pycroner.cli_colors import CliColorPicker


class Runner:
    def __init__(self, config_path="pycroner.yml", to_print=True):
        self.config_path = config_path
        self.printer = Printer(to_print=to_print)
        self.color_picker = CliColorPicker()
    
    def run(self):
        """Continuously schedule and execute jobs.

        Instead of looping every second and checking if a job should run, we
        calculate the next run time for each job and sleep until the earliest
        job is due. When multiple jobs share the same run time we execute all of
        them before scheduling the next iteration.
        """

        self.printer.write("\033[34m[pycroner]\033[0m running")
        jobs = load_config(self.config_path)

        config_last_modified_at = os.path.getmtime(self.config_path)

        # Min-heap ordered by the next run time for each job.
        job_runs: List[Tuple[datetime, JobSpec]] = []
        now = datetime.now()
        
        for job in jobs:
            heapq.heappush(job_runs, (self.__compute_next_run_time(job.schedule, now), job))

        while True:
            if not job_runs:
                time.sleep(60)
            else:
                next_time, _ = job_runs[0]
                now = datetime.now()
                
                sleep_for = (next_time - now).total_seconds()
                if sleep_for > 0:
                    time.sleep(sleep_for)

                now = datetime.now()
                due: List[Tuple[datetime, JobSpec]] = []
                
                while job_runs and job_runs[0][0] <= now:
                    _, job = heapq.heappop(job_runs)
                    due.append((now, job))

                for _, job in due:
                    for instance in job.expand():
                        self.printer.write(f"\033[34m[pycroner]\033[0m Running job: {job.id}")
                        self.__run_process(instance)

                    heapq.heappush(job_runs, (self.__compute_next_run_time(job.schedule, now), job,),)

            # Reload configuration if it has changed.
            config_new_modified_at = os.path.getmtime(self.config_path)
            if config_new_modified_at != config_last_modified_at:
                jobs = load_config(self.config_path)
                config_last_modified_at = config_new_modified_at
                job_runs = []
                now = datetime.now()
                
                for job in jobs:
                    heapq.heappush(job_runs, (self.__compute_next_run_time(job.schedule, now), job))

    def __compute_next_run_time(self, schedule: dict, start: datetime) -> datetime:
        """Compute the next datetime at which ``schedule`` should run.

        ``start`` is treated as an exclusive lower bound; the returned time will
        always be *after* ``start``. The calculation jumps between fields rather
        than iterating minute by minute, avoiding the busy-loop behaviour of the
        previous runner implementation.
        """

        current = start.replace(second=0, microsecond=0)
        if start.second or start.microsecond:
            current += timedelta(minutes=1)

        minutes = sorted(schedule["minute"])
        hours = sorted(schedule["hour"])
        weekdays = schedule["weekday"]
        months = sorted(schedule["month"])

        while True:
            # Month
            if current.month not in schedule["month"]:
                next_month = next((m for m in months if m > current.month), None)
                if next_month is None:
                    current = current.replace(year=current.year + 1, month=months[0], day=1, hour=0, minute=0,)
                else:
                    current = current.replace(month=next_month, day=1, hour=0, minute=0)

                continue

            # Day and weekday
            max_day = monthrange(current.year, current.month)[1]
            valid_days = sorted(d for d in schedule["day"] if d <= max_day)
            
            if not valid_days:
                # No valid day this month; advance to next month
                next_month = next((m for m in months if m > current.month), None)
                if next_month is None:
                    current = current.replace(year=current.year + 1, month=months[0], day=1, hour=0, minute=0,)
                else:
                    current = current.replace(month=next_month, day=1, hour=0, minute=0)

                continue

            if current.day not in valid_days or current.weekday() not in weekdays:
                current += timedelta(days=1)
                current = current.replace(hour=0, minute=0)

                continue

            # Hour
            if current.hour not in schedule["hour"]:
                next_hour = next((h for h in hours if h > current.hour), None)
                if next_hour is None:
                    current += timedelta(days=1)
                    current = current.replace(hour=hours[0], minute=0)
                else:
                    current = current.replace(hour=next_hour, minute=0)
                continue

            # Minute
            if current.minute not in schedule["minute"]:
                next_minute = next((m for m in minutes if m > current.minute), None)
                if next_minute is None:
                    current += timedelta(hours=1)
                    current = current.replace(minute=minutes[0])
                else:
                    current = current.replace(minute=next_minute)
                continue

            return current

    def __run_process(self, instance: JobInstance):
        try: 
            proc = subprocess.Popen(
                instance.command,
                shell=False,
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
            )

            color = self.color_picker.get(instance.id)
            prefix = f'{color}[{instance.id}]\033[0m: '
            for line in proc.stdout:
                self.printer.write(prefix + line.rstrip())

        except Exception as e: 
            self.printer.write(f"\033[34m[pycroner]\033[0m: Failed to run job: {instance.id}")
            self.printer.write(f"\033[34m[pycroner]\033[0m: Error: {e}")
