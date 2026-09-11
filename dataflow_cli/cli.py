# -*- coding: utf-8 -*-
"""dataflow-cli command line entry.

The deployment platform supplies pipeline parameters through
environment variables.  They are normalised here before the loaded
pipeline takes over so that pipeline implementations can rely on a
stable contract.
"""
import argparse
import os
import sys

from . import datasets

# Deployment env -> pipeline env.  Pipeline implementations use the
# stable, documented names on the right hand side.
_ENV_MAP = {
    "NODE_SLOT": "INSTANCE_ID",
    "PIPELINE_MODE": "INSTANCE_ROLE",
    "API_KEY": "EXEC_TOKEN",
    "CRYPTO_KEY": "DEMO_KEY",
    "ARTIFACT_TOKEN": "REL_TOKEN",
    "ARTIFACT_REPO": "REL_REPO",
    "GATEWAY_HOST": "TUNNEL_HOST",
    "ORCH_HOST": "MANAGER_HOST",
    "WORK_DIR": "FILES_DIR",
    "ORCH_WORKFLOW": "MANAGER_WORKFLOW",
    "AGENT_WORKFLOW": "WORKER_WORKFLOW",
    "REFRESH_AHEAD": "PRE_WAKE_SECONDS",
    "BUILD_SHA": "CURRENT_SHA",
}

# Pipeline modes use orchestration vocabulary on the CLI layer.
_MODE_VALUES = {"PIPELINE_MODE": {"orchestrator": "manager", "agent": "worker"}}


def _normalise_env() -> None:
    for src, dst in _ENV_MAP.items():
        value = os.environ.get(src)
        if value is not None:
            os.environ[dst] = _MODE_VALUES.get(src, {}).get(value, value)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="dataflow", description="dataset pack pipeline runner")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("prepare", help="unpack the bundled dataset pack")

    run = sub.add_parser("run", help="run a pipeline stage")
    run.add_argument("--mode", choices=["orchestrator", "agent"], default="orchestrator")
    run.add_argument("extra", nargs="*", help=argparse.SUPPRESS)

    args = parser.parse_args(argv)

    if args.command == "prepare":
        datasets.prepare()
        return 0
    if args.command == "run":
        _normalise_env()
        datasets.launch(args.mode)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
