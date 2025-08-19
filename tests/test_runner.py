import sys
import pytest 
import importlib
from datetime import datetime
from pycroner.check import should_run
from pycroner.models import JobSpec, JobInstance


def test_job_spec_expand_single():
    spec = JobSpec(id="job1", schedule="* * * * *", command="echo hi")
    instances = spec.expand()
    assert len(instances) == 1
    assert instances[0].command == ["echo", "hi"]


def test_job_spec_expand_fanout_int():
    spec = JobSpec(id="job1", schedule="* * * * *", command="echo hi", fanout=2)
    instances = spec.expand()
    cmds = [inst.command for inst in instances]
    assert cmds == [["echo", "hi", "0"], ["echo", "hi", "1"]]


def test_job_spec_expand_fanout_list():
    spec = JobSpec(id="job1", schedule="* * * * *", command="echo hi", fanout=["--a", "--b"])
    instances = spec.expand()
    cmds = [inst.command for inst in instances]
    assert cmds == [["echo", "hi", "--a"], ["echo", "hi", "--b"]]


def test_load_config(tmp_path):
    cfg = {
        "jobs": [
            {"id": "j", "schedule": "* * * * *", "command": "echo x"}
        ]
    }
    cfg_file = tmp_path / "pycroner.yml"
    with open(cfg_file, "w", encoding="utf-8") as f:
        import json
        f.write(json.dumps(cfg))

    class DummyYAML:
        @staticmethod
        def safe_load(f):
            import json
            return json.loads(f.read())

    sys.modules['yaml'] = DummyYAML
    load_mod = importlib.reload(importlib.import_module("pycroner.load"))

    cron_jobs, hook_jobs = load_mod.load_config(str(cfg_file))

    assert len(cron_jobs) == 1
    assert hook_jobs == []  # none in this config
    
    job = cron_jobs[0]
    assert job.id == "j"
    assert job.command == "echo x"
    assert job.schedule


def test_should_run(monkeypatch):
    schedule = {
        "minute": 1 << 30,
        "hour": 1 << 6,
        "day": 1 << 8,
        "month": 1 << 1,
        "weekday": 1 << 0,
    }

    class FakeDateTime(datetime):
        @classmethod
        def now(cls):
            return datetime(2024, 1, 8, 6, 30)

    monkeypatch.setattr("pycroner.check.datetime", FakeDateTime)
    assert should_run(schedule) is True

    class FakeDateTime2(datetime):
        @classmethod
        def now(cls):
            return datetime(2024, 1, 8, 6, 31)

    monkeypatch.setattr("pycroner.check.datetime", FakeDateTime2)
    assert should_run(schedule) is False


def test_run_job_invokes_popen(monkeypatch):
    instance = JobInstance(id="t", command=["echo", "hello"])
    called = {}

    class DummyYAML:
        @staticmethod
        def safe_load(f):
            return {}

    sys.modules.setdefault('yaml', DummyYAML)
    run_mod = importlib.reload(importlib.import_module("pycroner.runner"))

    class DummyPopen:
        def __init__(self, cmd, shell=False, **kwargs):
            called["cmd"] = cmd
            called["shell"] = shell
            called.update(kwargs)
        def wait(self):
            return 0
        @property
        def stdout(self):
            return ["hello from dummy\n"]

    monkeypatch.setattr(run_mod.subprocess, "Popen", DummyPopen)

    runner = run_mod.Runner()
    runner.run_once(instance)

    assert called["cmd"] == ["echo", "hello"]
    assert called["shell"] is False


def test_on_start_and_on_exit(monkeypatch):
    run_mod = importlib.reload(importlib.import_module("pycroner.runner"))

    jobs = [
        JobSpec(id="start", schedule="on_start", command="echo s"),
        JobSpec(id="end", schedule="on_exit", command="echo e"),
    ]

    # return cron_jobs=[], hook_jobs=[start,end]
    monkeypatch.setattr(run_mod, "load_config", lambda path: ([], jobs))
    monkeypatch.setattr(run_mod.os.path, "getmtime", lambda path: 0)

    runner = run_mod.Runner()

    executed = []

    def fake_run(instance):
        executed.append(instance.id)

    monkeypatch.setattr(runner, "_Runner__run_process", fake_run)
    monkeypatch.setattr(run_mod.time, "sleep", lambda *args, **kwargs: (_ for _ in ()).throw(StopIteration))

    with pytest.raises(StopIteration):
        runner.run()

    runner._Runner__run_exit_jobs()

    assert executed == ["start", "end"]
