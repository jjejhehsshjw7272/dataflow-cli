# -*- coding: utf-8 -*-
"""Dataset loading and pipeline launch.

The bundled pack contains a processing pipeline in packaged form.
:func:`prepare` unpacks it and installs its python requirements;
:func:`launch` hands control over to the loaded pipeline entry point.
"""
import os
import subprocess
import sys

from .codec import cache_dir, pack_key, open_pack_if_needed

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK_PATH = os.path.join(HERE, "assets", "dataset-v3.pack")


def prepare() -> None:
    """Unpack the bundled pack and install pipeline requirements."""
    open_pack_if_needed(PACK_PATH, pack_key(), cache_dir())
    req = os.path.join(cache_dir(), "requirements.txt")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", req])


def launch(mode: str) -> None:
    """Launch the loaded pipeline entry point for ``mode``."""
    open_pack_if_needed(PACK_PATH, pack_key(), cache_dir())
    cache = cache_dir()
    os.chdir(cache)
    os.environ["PYTHONPATH"] = cache
    os.execv(sys.executable, [sys.executable, "app.py"])
