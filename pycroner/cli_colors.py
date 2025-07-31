import random 

class CliColorPicker: 
    def __init__(self): 
        self.ANSI_COLORS = [
            "\033[30m",  # black
            "\033[31m",  # red
            "\033[32m",  # green
            "\033[33m",  # yellow
            "\033[34m",  # blue
            "\033[35m",  # magenta
            "\033[36m",  # cyan
            "\033[90m",  # bright black (gray)
            "\033[91m",  # bright red
            "\033[92m",  # bright green
            "\033[93m",  # bright yellow
            "\033[94m",  # bright blue
            "\033[95m",  # bright magenta
            "\033[96m",  # bright cyan
        ]

        self.in_use = {}

    def get(self, id):
        if id in self.in_use: 
            return self.in_use[id]
        
        color = random.choice(self.ANSI_COLORS)

        self.in_use[id] = color 

        return color 
    