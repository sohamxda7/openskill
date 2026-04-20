# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import os
import stat
import tempfile


MAX_EDITOR_FILE_BYTES = 10 * 1024 * 1024


def read_editor_file(path, max_bytes=MAX_EDITOR_FILE_BYTES):
    if os.path.getsize(path) > max_bytes:
        raise OSError("file is too large to open in the editor")
    with open(path, "rb") as handle:
        if b"\0" in handle.read(8192):
            raise ValueError("file appears to be binary")
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read()


def write_editor_file(path, content):
    target_path = os.path.realpath(path) if os.path.islink(path) else path
    directory = os.path.dirname(os.path.abspath(target_path)) or "."
    prefix = os.path.basename(target_path) + "."
    existing_mode = None
    if os.path.exists(target_path):
        existing_mode = stat.S_IMODE(os.stat(target_path).st_mode)
    file_descriptor, temp_path = tempfile.mkstemp(dir=directory, prefix=prefix, suffix=".tmp")
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, target_path)
        if existing_mode is not None:
            os.chmod(target_path, existing_mode)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
