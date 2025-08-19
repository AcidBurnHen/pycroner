from typing import List, Set, Dict, Union 

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

        self.HOOKS = {
            "on_start", 
            "on_exit",
        }

    def parse(self, expr: str) -> Union[str, Dict[str, int]]:
        expr = expr.strip()
        if expr in self.HOOKS:
            return expr 
        
        parts = expr.split()
        if len(parts) != 5: 
            raise ValueError(f"Expected 5 fields in cron expression, got: {len(parts)}, please provide a proper cron expression")
        
        parsed: Dict[str, int] = {}
        for i, field in enumerate(self.FIELD_NAMES):
            start, end = self.FIELD_RANGES[field]
            parsed[field] = self.__parse_field(parts[i], start, end)

        return parsed
    
    def __parse_field(self, part: str, start: int, end: int) -> int: 
        # Result is now a bitmask to save on memory
        result = 0

        for expr_part in part.split(','):
            if expr_part == '*':
                result |= self.__range_mask(start, end)
            elif expr_part.startswith('*/'):
                step = int(expr_part[2:])
                result |= self.__range_mask(start, end, step)
            elif '-' in expr_part:
                a_str, b_str = expr_part.split('-')
                a, b = int(a_str), int(b_str)
                if a > b or not (start <= a <= end) or not (start <= b <= end):
                    raise ValueError(f"Invalid range: {a}-{b}")
                
                result |= self.__range_mask(a, b)
            else: 
                val = int(expr_part)
                if not (start <= val <= end):
                    raise ValueError(f"Invalid value: {val}")
                
                result |= 1 << val 

        return result 
    
    @staticmethod
    def __range_mask(start: int, end: int, step: int = 1) -> int: 
        mask = 0
        for v in range(start, end + 1, step):
            mask |= 1 << v 

        return mask 
        