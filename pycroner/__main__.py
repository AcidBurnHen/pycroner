import argparse
import os
from pathlib import Path
from pycroner.runner import Runner

def main(argv=None):
    parser = argparse.ArgumentParser(description="Run pycroner jobs")
    
    parser.add_argument("--at", dest="at", default=".", help="Directory containing the config and relative job commands")
    parser.add_argument("--config", dest="config", help="Path to configuration file")
    
    args = parser.parse_args(argv)

    working_dir = Path(args.at).resolve()
    os.chdir(working_dir)

    config_path = Path(args.config) if args.config else working_dir / "pycroner.yml"
    
    runner = Runner(str(config_path))
    runner.run()

def cli_entrypoint():
    main()