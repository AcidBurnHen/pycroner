from typing import List, Set, Dict 

class CronParser:
    def __init__(self):
        self.FIELD_NAMES = ["minute", "hour", "day",  "month", "weekday"]
        self.FIELD_RANGES = {
            "minute":  (0, 59),
            "hour":    (0, 23),
            "day":     (1, 31),
            "month":   (1, 12),
            "weekday": (0, 6)
        }        

    def parse(self, expr: str) -> Dict[str, Set[int]]:
        parts = expr.strip().split()
        if len(parts) != 5: 
            raise ValueError(f"Expected 5 fields in cron expression, got: {len(parts)}, please provide a proper cron expression")
        
        parsed = {}
        for i, field in enumerate(self.FIELD_NAMES):
            part = parts[i]
            field_range = self.FIELD_RANGES[field]

            parsed[field] = self.__parse_field(part, field_range)

        return parsed
    
    def __parse_field(self, part: str, field_range: tuple[int, int]) -> Set[int]: 
        result = set()

        for expr_part in part.split(','):
            start, end = field_range

            if expr_part == '*':
                result.update(set(range(start, end + 1)))
            elif expr_part.startswith('*/'):
                step = int(expr_part[2:])
                result.update(set(range(start, end + 1, step)))
            elif '-' in expr_part:
                a, b = expr_part.split('-')
                a, b = int(a), int(b)
                if a > b or not (start <= a <= end) or not (start <= b <= end):
                    raise ValueError(f"Invalid range: {a}-{b}")
                
                result.update(set(range(a, b + 1)))
            else: 
                val = int(expr_part)
                if not (start <= val <= end):
                    raise ValueError(f"Invalid value: {val}")
                
                result.update({val})

        return result 
        