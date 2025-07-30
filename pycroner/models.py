import shlex
from dataclasses import dataclass
from typing import Union, List

@dataclass
class JobInstance: 
    id: str 
    command: List[str]

@dataclass
class JobSpec:
    id: str 
    schedule: str 
    command: str 
    fanout: Union[int, List[str], None] = None 

    def expand(self) -> List[JobInstance]:
        if self.fanout is None: 
            return [JobInstance(id=self.id, command=shlex.split(self.command))]

        if isinstance(self.fanout, list):
            jobs = []
            for args in self.fanout: 
                jobs.append(JobInstance(id=self.id, command=shlex.split(f"{self.command} {args}")))
            
            return jobs  
        
        if isinstance(self.fanout, int): 
            jobs = []
            for i in range(self.fanout): 
                jobs.append(JobInstance(id=self.id, command=shlex.split(f"{self.command} {i}")))

            return jobs 
        
        raise ValueError(f"Invalid fanout for job: '{self.id}': {self.fanout}")
