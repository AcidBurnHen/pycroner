import os
import time 
import subprocess
from datetime import datetime
from pycroner.load import load_config
from pycroner.check import should_run
from pycroner.models import JobInstance
from pycroner.printer import Printer
from pycroner.cli_colors import CliColorPicker


class Runner: 
    def __init__(self, config_path="pycroner.yml", to_print=True):
        self.config_path = config_path
        self.printer = Printer(to_print=to_print)
        self.color_picker = CliColorPicker()
    
    def run(self): 
        self.printer.write("\033[34m[pycroner]\033[0m running")
        jobs = load_config(self.config_path)

        last_minute = None 
        config_last_modified_at = os.path.getmtime(self.config_path)
        while True: 
            now = datetime.now()
            current_minute = (now.year, now.month, now.day, now.hour, now.minute)

            if current_minute != last_minute: 
                last_minute = current_minute
                
                config_new_modified_at = os.path.getmtime(self.config_path)
                if config_new_modified_at != config_last_modified_at: 
                    jobs = load_config(self.config_path)
                    config_last_modified_at = config_new_modified_at

                for job in jobs: 
                    if not should_run(job.schedule): 
                        continue

                    for instance in job.expand():
                        self.printer.write(f"\033[34m[pycroner]\033[0m Running job: {job.id}")
                        self.__run_process(instance)

                time.sleep(1)

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


