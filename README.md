![Pycroner](icon.png)
# Pycroner

**Pycroner** is a lightweight cron style job runner implemented in Python.
Jobs are configured via a YAML file and executed by the runner once their
cron schedule matches the current time.

## Features
- Parses standard five field cron expressions (minute, hour, day, month, weekday)
  using a small built in parser.
- Jobs can optionally be *fanned out* into multiple processes. Fanout may be an
  integer (repeat the job N times) or a list of argument strings that will be
  appended to the base command.
- Configuration lives in `pycroner.yml` by default. The exact format is
  described in [`pycroner/spec.md`](pycroner/spec.md).

## Installation

From PyPI:

```bash
pip install pycroner
```

## Usage
### From code 
1. Create a `pycroner.yml` file describing your jobs. A simple example is shown
   below.
2. Run the job runner from a Python script:

```python
from pycroner.runner import run

run("pycroner.yml")
```

The runner checks schedules every minute and spawns each job as a subprocess
when its cron expression matches the current time.

### From CLI
You can also invoke the runner directly from the command line using the
`pycroner` command. By default it looks for `pycroner.yml` in the current
directory:

```bash
pycroner
```

Specify an alternative working directory with `--at` or a specific
configuration file with `--config`:

```bash
pycroner --at /path/to/project
pycroner --config custom.yml
```

## Example Configuration
```yaml
jobs:
  - id: "index_articles"
    schedule: "*/15 * * * *"
    command: "python index.py"
    fanout: 4

  - id: "daily_etl"
    schedule: "0 2 * * *"
    command: "python etl.py"
    fanout:
      - "--source=internal --mode=full"
      - "--source=external --mode=delta"

  - id: "ping"
    schedule: "* * * * *"
    command: "python ping.py"
```

Jobs run independently, and any output or error handling is left to your
commands. For full details see [`pycroner/spec.md`](pycroner/spec.md).
