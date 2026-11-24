#!/usr/bin/env python3
"""Absurd Micro-Startup Pitch-Off - one-sentence pitch for lazy AI agents.

Pure Python 3.13 standard library. The program writes one pitch sentence to
/output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt). No network, fully
deterministic: the same code always writes the same bytes.

The pitch (142 characters, no trailing newline):
    FailFarm sells your lazy agent's failed tool calls to AI labs as
    training data at $0.02 a failure, so it earns money by never once
    succeeding.

Usage: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import tempfile

PITCH = (
    "FailFarm sells your lazy agent's failed tool calls to AI labs as "
    "training data at $0.02 a failure, so it earns money by never once "
    "succeeding."
)


def _write_all(fd, data):
    """Write every byte of data to fd, coping with partial writes."""
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        if written == 0:
            raise OSError("short write: wrote 0 bytes")
        view = view[written:]


def _write_entry(out_dir):
    """Atomically write entry.txt (mode 0644) into out_dir.

    The output directory itself is never removed (the grader mounts it);
    its previous contents are cleared first so no stale file survives.
    """
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
    final = os.path.join(out_dir, "entry.txt")
    data = PITCH.encode("utf-8")
    last_error = None
    for _attempt in range(3):
        fd = None
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(
                prefix=".entry.txt.", dir=out_dir
            )
            _write_all(fd, data)
            os.fsync(fd)
            os.close(fd)
            fd = None
            os.chmod(tmp_path, 0o644)
            os.replace(tmp_path, final)
            tmp_path = None
            os.chmod(final, 0o644)
            return
        except OSError as exc:  # stale tmp file: retry with a fresh one
            last_error = exc
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if tmp_path is not None:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
    raise last_error


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    _write_entry(out_dir)


if __name__ == "__main__":
    main()
