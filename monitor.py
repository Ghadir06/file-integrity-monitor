import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from config import MONITOR_DIR, BASELINE_FILE, LOG_FILE



# SHA-256 each file - read in chunks so big files don't kill memory
def hash_file(path: Path) -> str:
    # read in chunks so it doesn't load the whole file into memory 
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def build_baseline(directory: Path) -> dict:
    files = {}
    for p in directory.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(directory))
            files[rel] = hash_file(p)
    return files

def save_baseline(baseline: dict):
    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=4)
    print(f"baseline saved ({len(baseline)} files)")

def load_baseline() -> dict:
    if not BASELINE_FILE.exists():
        print("no baseline yet then run option 1 first")
        return {}
    with open(BASELINE_FILE) as f:
        return json.load(f)

def log_alert(msg: str):
    LOG_FILE.parent.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def check_integrity(directory: Path) -> list:
    baseline = load_baseline()
    if not baseline:
        return []

    current = build_baseline(directory)
    alerts = []

    # check what was there before
    for path, old_hash in baseline.items():
        if path not in current:
            alerts.append(f"DELETED: {path}")
        elif current[path] != old_hash:
            # hash changed so something was modified
            alerts.append(f"MODIFIED: {path}")

    # second loop so we catch anything that wasn't in the baseline at all
    for path in current:
        if path not in baseline:
            alerts.append(f"NEW FILE: {path}")

    for a in alerts:
        log_alert(a)

    if not alerts:
        log_alert("all good there were no changes detected")
    return alerts

def main():
    MONITOR_DIR.mkdir(exist_ok=True)

    if "--create-baseline" in sys.argv:
        baseline = build_baseline(MONITOR_DIR)
        save_baseline(baseline)
    elif "--check" in sys.argv:
        check_integrity(MONITOR_DIR)
    elif "--watch" in sys.argv:
        from watcher import start_watcher
        start_watcher()
    else:
        print("Usage:")
        print("  python monitor.py --create-baseline")
        print("  python monitor.py --check")
        print("  python monitor.py --watch")

if __name__ == "__main__":
    main()