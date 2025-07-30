# pycroner YAML Configuration Spec

## Overview
This document defines the structure and expected behavior of the `pycroner.yml` configuration file used by the `pycroner` job runner.

## File Name
- Default: `pycroner.yml`
- Optional override via CLI: `--config=your_file.yml`

## Top-Level Structure
```yaml
jobs:
  - id: string               # Required, unique job identifier
    schedule: string         # Required, crontab-style schedule string
    command: string          # Required, base shell command to execute
    fanout:                  # Optional, integer or list of argument strings
```

## Fields

### `id`
- **Type**: `string`
- **Required**: Yes
- **Description**: A unique identifier for the job. Used internally and for logging.

### `schedule`
- **Type**: `string`
- **Required**: Yes
- **Format**: Standard 5-field crontab syntax
  - `minute hour day month weekday`
  - Examples:
    - `* * * * *` → every minute
    - `0 0 * * *` → daily at midnight
    - `*/5 * * * *` → every 5 minutes
- **Note**: evaluated using `croniter`

### `command`
- **Type**: `string`
- **Required**: Yes
- **Description**: The shell command to be executed. This command will be passed to `subprocess.Popen` and executed as-is.
- **Behavior**:
  - No escaping or argument substitution is done.
  - The job runner is responsible for splitting or executing this as appropriate per OS.

### `fanout`
- **Type**: `integer` or `list of strings`
- **Required**: No
- **Default**: `None`

#### Fanout as Integer
```yaml
fanout: 3
```
- Spawns the same `command` 3 times in parallel with no extra arguments.

#### Fanout as List of Strings
```yaml
fanout:
  - "--env=prod --sync=full"
  - "--env=dev --sync=partial"
```
- For each list item, a job is spawned as:
  ```
  {command} {fanout_item}
  ```
  Example result:
  ```bash
  python sync.py --env=prod --sync=full
  python sync.py --env=dev --sync=partial
  ```

## Example Config
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

## Notes
- All fields are case-sensitive
- Jobs are evaluated every minute by default
- Fanout expands the command into multiple parallel jobs
- Jobs are run as subprocesses; failure or output handling is up to the runner

