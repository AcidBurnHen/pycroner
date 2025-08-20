import queue
import threading
import os
import sys
import subprocess
import time

# Windows-specific
if os.name == "nt":
    import msvcrt
    import ctypes
    from ctypes import wintypes

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _PeekNamedPipe = _kernel32.PeekNamedPipe
    _PeekNamedPipe.argtypes = [wintypes.HANDLE,
                               wintypes.LPVOID,
                               wintypes.DWORD,
                               wintypes.LPVOID,
                               ctypes.POINTER(wintypes.DWORD),
                               wintypes.LPVOID]
    _PeekNamedPipe.restype = wintypes.BOOL

    def pipe_has_data(fd):
        """Check if pipe has data (Windows)."""
        handle = msvcrt.get_osfhandle(fd)
        avail = wintypes.DWORD()
        ok = _PeekNamedPipe(handle, None, 0, None, ctypes.byref(avail), None)
        if not ok:
            return False
        return avail.value > 0
else:
    def pipe_has_data(fd):
        """On POSIX, just use select() internally."""
        import select
        r, _, _ = select.select([fd], [], [], 0)
        return bool(r)


class Logger(threading.Thread):
    def __init__(self, printer):
        super().__init__(name="Logger", daemon=True)
        self.printer = printer
        self.cmd_queue = queue.Queue()
        self._stopping = threading.Event()
        self._watched = []

    def run(self):
        while not self._stopping.is_set():
            # collect new processes
            try:
                while True:
                    fd, prefix, proc = self.cmd_queue.get_nowait()
                    self._watched.append((fd, prefix, proc))
                # drain queue
            except queue.Empty:
                pass

            # check each watched fd
            still_watching = []
            for fd, prefix, proc in self._watched:
                if pipe_has_data(fd.fileno()):
                    line = fd.readline()
                    if line:
                        self.printer.write(prefix + line.rstrip())
                        still_watching.append((fd, prefix, proc))
                    else:
                        fd.close()
                        proc.wait()
                else:
                    still_watching.append((fd, prefix, proc))
            self._watched = still_watching

            time.sleep(0.05)  # small tick

    def watch(self, proc, prefix):
        if not proc.stdout:
            raise ValueError("Process must be started with stdout=PIPE")
        self.cmd_queue.put((proc.stdout, prefix, proc))

    def shutdown(self):
        self._stopping.set()
