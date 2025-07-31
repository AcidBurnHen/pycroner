class Printer: 
    def __init__(self, to_print: bool = False):
        self.to_print = to_print

    def write(self, *args): 
        if not self.to_print: 
            return 
        
        print(*args)