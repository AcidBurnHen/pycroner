import yaml 
from typing import List 
from pathlib import Path 
from pycroner.models import JobSpec
from pycroner.parser import CronParser

def load_config(path: str) -> List[JobSpec]:
    with open(Path(path), 'r', encoding='utf-8') as f: 
        config = yaml.safe_load(f)

    if not isinstance(config, dict) or 'jobs' not in config: 
        raise ValueError("Invalid config format. Expected 'jobs' at top level.")

    parser = CronParser()
    job_specs = []
    for job in config['jobs']: 
        job_specs.append(JobSpec(
            id=job['id'],
            schedule=parser.parse(job['schedule']),
            command=job['command'],
            fanout=job.get('fanout'),
        ))

    return job_specs
