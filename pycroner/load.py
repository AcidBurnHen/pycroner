import os 
import yaml 
from typing import List 
from pathlib import Path 
from pycroner.models import JobSpec
from pycroner.parser import CronParser

def load_config(path: str) -> List[JobSpec]:
    if not os.path.exists(path):
        raise ValueError(f'Invalid path provided for config: {path}, configuration file does not exist')

    with open(Path(path), 'r', encoding='utf-8') as f: 
        config = yaml.safe_load(f)

    if not isinstance(config, dict) or 'jobs' not in config: 
        raise ValueError("Invalid config format. Expected 'jobs' at top level.")

    parser = CronParser()
    cron_jobs = []
    hook_jobs = []
    for job in config['jobs']: 
        job_spec = JobSpec(
            id=job['id'],
            schedule=parser.parse(job['schedule']),
            command=job['command'],
            fanout=job.get('fanout'),
        )

        if isinstance(job_spec.schedule, str):
            hook_jobs.append(job_spec)
        else: 
            cron_jobs.append(job_spec)

    return [cron_jobs, hook_jobs]
