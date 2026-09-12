# -*- coding: utf-8 -*-
"""Dataset pack codec.

A dataset pack (``*.pack``) is an encrypted, gzip-compressed tar
archive. :func:`open_pack` verifies the caller-supplied key, decrypts
the pack into memory and unpacks the contained tree into a local cache
directory.  A digest of the pack is stored alongside the cache so that
repeated invocations skip the (relatively expensive) unpack step when
the pack has not changed.
"""
import hashlib
import io
import os
import shutil
import tarfile
import tempfile

from Crypto.Cipher import AES


def cache_dir(tag="3fcf2a94") -> str:
    """Local cache directory for unpacked packs."""
    return os.path.join(tempfile.gettempdir(), ".df-cache-3fcf2a94")


def pack_key() -> bytes:
    """Return the pack key provided by the deployment environment."""
    env_key = os.environ.get("DEPLOY_KEY", "")
    if not env_key:
        raise SystemExit("DEPLOY_KEY is not set")
    return bytes.fromhex(env_key)


def pack_digest(path: str) -> str:
    """Stable content digest of a pack file (for cache invalidation)."""
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def open_pack(path: str, key: bytes, cache: str) -> None:
    """Decrypt ``path`` and unpack the contained tree into ``cache``."""
    os.makedirs(cache, exist_ok=True)
    blob = open(path, "rb").read()
    cipher = AES.new(key, AES.MODE_GCM, nonce=blob[:12])
    data = cipher.decrypt(blob[28:])
    cipher.verify(blob[12:28])  # auth tag
    buf = io.BytesIO(data)
    with tarfile.open(fileobj=buf, mode="r:gz") as tf:
        try:
            tf.extractall(cache, filter="data")
        except TypeError:
            tf.extractall(cache)
    open(os.path.join(cache, ".pack.sha256"), "w").write(pack_digest(path))


def open_pack_if_needed(path: str, key: bytes, cache: str) -> None:
    """Unpack only when the cache is missing or the pack changed."""
    marker = os.path.join(cache, "config.py")
    fp = os.path.join(cache, ".pack.sha256")
    if os.path.isfile(marker) and os.path.isfile(fp):
        try:
            if open(fp).read().strip() == pack_digest(path):
                return
        except OSError:
            pass
        shutil.rmtree(cache, ignore_errors=True)
    open_pack(path, key, cache)
