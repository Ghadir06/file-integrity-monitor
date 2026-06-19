# File-Integrity-Monitor

A Python tool that watches a directory and detects when files are created, modified, or deleted using SHA-256 hashing to catch any changes at the byte level. It runs in two modes: a one-off integrity check against a saved baseline, or a real-time watcher that alerts you the moment something changes.

I built this as a solo project to get hands-on with some concepts from my security modules, specifically how file integrity monitoring actually works under the hood (it's basically what tools like Tripwire do).


## How It Works

When you create a baseline, the tool walks the target directory, hashes every file with SHA-256, and saves the results to `baseline.json`. When you run a check (or have the watcher running), it compares the current state against that snapshot and flags anything that's changed.

- **new file** → hash exists now but not in the baseline  
- **modified file** → hash exists in both but they don't match  
- **deleted file** → hash was in the baseline but the file is gone  

All alerts get timestamped and written to `logs/alerts.log`.

The real-time watcher uses [watchdog](https://github.com/gorakhargosh/watchdog) to listen for filesystem events rather than polling, so it reacts instantly instead of running on a timer.


## Project Structure

```
file-integrity-monitor/
├── monitor.py          # hashing, baseline management, integrity checks
├── watcher.py          # real-time watchdog event handler
├── config.py           # paths (monitor dir, baseline file, log file)
├── requirements.txt
├── logs/
│   └── alerts.log
└── test_folder/        # the directory being monitored
    └── example.txt
```


## Setup

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/your-username/file-integrity-monitor.git
cd file-integrity-monitor
python3 -m venv .venv
source .venv/bin/activate       # windows: .venv\Scripts\activate
pip install -r requirements.txt
```


## Usage

**1. Create a baseline**

Scans `test_folder` and saves a hash snapshot to `baseline.json`

```bash
python monitor.py --create-baseline
```

**2. Run a manual integrity check**

Compares current state against the baseline and prints any differences

```bash
python monitor.py --check
```

**3. Start the real-time watcher**

Listens for filesystem events and logs alerts as they happen. Open a second terminal to trigger test events while this is running

```bash
python monitor.py --watch
```


## Example Output

Alerts print to the terminal and get saved to `logs/alerts.log`:

```
[2026-06-19 19:02:42] NEW FILE: test.txt
[2026-06-19 19:02:58] MODIFIED: example.txt
[2026-06-19 19:03:19] DELETED: test.txt
```

<img width="1834" height="120" alt="image" src="https://github.com/user-attachments/assets/911fdf54-689a-4b71-a973-e3a75ff42abd" />



<img width="1864" height="184" alt="image" src="https://github.com/user-attachments/assets/84078423-8782-4202-9f38-77e1f8c4fe2d" />


## Changing the Monitored Directory

Edit `config.py`:

```python
from pathlib import Path

MONITOR_DIR = Path("your_folder_here")
BASELINE_FILE = Path("baseline.json")
LOG_FILE = Path("logs/alerts.log")
```


## Dependencies

- [watchdog](https://pypi.org/project/watchdog/) — filesystem event monitoring  
- Everything else (`hashlib`, `json`, `pathlib`) is standard library

```
watchdog==6.0.0
```


## What I Learned

- How SHA-256 hashing works in practice and why reading files in chunks matters for memory efficiency
- The difference between polling-based and event-driven monitoring
- How tools like Tripwire and AIDE approach file integrity at a conceptual level
- Pathlib for cross-platform file handling
- Structuring a Python project across multiple modules with a shared config


## Possible Improvements

- Email alerts when changes are detected (SMTP via `smtplib`)
- Exclude patterns for ignoring certain files or directories
- Scheduled checks via cron instead of manual runs
- Swap `baseline.json` for SQLite once the number of tracked files gets large


## License

MIT
