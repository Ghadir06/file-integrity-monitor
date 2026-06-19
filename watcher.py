import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from config import MONITOR_DIR
from monitor import hash_file, load_baseline, log_alert


class IntegrityHandler(FileSystemEventHandler):

    def __init__(self):
        # load once at startup and keep in memory
        self.baseline = load_baseline()
        self.monitor_dir = MONITOR_DIR.resolve()

    def get_relative_path(self, event_path):
        path = Path(event_path).resolve()
        return str(path.relative_to(self.monitor_dir))

    def on_modified(self, event):
        if event.is_directory:
            return
        try:
            rel = self.get_relative_path(event.src_path)
            old = self.baseline.get(rel)
            new = hash_file(self.monitor_dir / rel)

            # only flag it if we've seen this file before and the hash actually changed
            if old and old != new:
                log_alert(f"MODIFIED: {rel}")
                self.baseline[rel] = new

        except FileNotFoundError:
            pass

    def on_created(self, event):
        if event.is_directory:
            return

        rel = self.get_relative_path(event.src_path)
        self.baseline[rel] = hash_file(self.monitor_dir / rel)
        log_alert(f"NEW FILE: {rel}")

    def on_deleted(self, event):
        if event.is_directory:
            return

        rel = self.get_relative_path(event.src_path)
        if rel in self.baseline:
            del self.baseline[rel]

        log_alert(f"DELETED: {rel}")


def start_watcher():
    MONITOR_DIR.mkdir(exist_ok=True)
    monitor_dir = MONITOR_DIR.resolve()

    print(f"watching {monitor_dir} - ctrl+c to stop")
    handler = IntegrityHandler()
    observer = Observer()
    observer.schedule(handler, str(monitor_dir), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()