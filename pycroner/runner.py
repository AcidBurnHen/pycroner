import time 
import subprocess
from datetime import datetime
from pycroner.load import load_config
from pycroner.check import should_run
from pycroner.models import JobInstance

def run(config_path="pycroner.yml"): 
    jobs = load_config(config_path)

    last_minute = None 

    while True: 
        now = datetime.now()
        current_minute = (now.year, now.month, now.day, now.hour, now.minute)

        if current_minute != last_minute: 
            last_minute = current_minute
            
            for job in jobs: 
                if not should_run(job.schedule): 
                    continue

                for instance in job.expand():
                    run_job(instance)

            time.sleep(1)

def run_job(instance: JobInstance): 
    try: 
        subprocess.Popen(
            instance.command,
            shell=True
        )
    except Exception as e: 
        print(f"[pycroner]: Failed to run job: {instance.id}")
        print(f"[prycroner]: Error: {e}")


