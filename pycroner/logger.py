import queue
import threading
import selectors

class Logger(threading.Thread):
    def __init__(self, printer):
        super().__init__(name="Logger", daemon=True)
        
        self.printer = printer
        self.selector = selectors.DefaultSelector()
        self.cmd_queue = queue.Queue()
        self._stopping = threading.Event()

    def run(self):
        while not self._stopping.is_set():
            # Register any new pipes
            try:
                while True:
                    fd, prefix, proc = self.cmd_queue.get_nowait()
                    self.selector.register(fd, selectors.EVENT_READ, (prefix, proc))
            except queue.Empty:
                pass

            # Wait for either output or timeout
            for key, _ in self.selector.select(timeout=0.5):
                prefix, proc = key.data
                line = key.fileobj.readline()
                
                if line:
                    self.printer.write(prefix + line.rstrip())
                else:
                    self.selector.unregister(key.fileobj)
                    key.fileobj.close()
                    proc.wait()

    def watch(self, proc, prefix):
        if not proc.stdout:
            raise ValueError("Process must be started with stdout=PIPE")
        
        self.cmd_queue.put((proc.stdout, prefix, proc))

    def shutdown(self):
        self._stopping.set()
