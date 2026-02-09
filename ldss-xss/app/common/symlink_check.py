import os

def symlink_check(path: str, allowed_base: str) -> None:
    if os.path.lexists(path) and os.path.islink(path):
        raise RuntimeError(f"Refusing symlink at {path!r}")
    if os.path.exists(path) and os.path.isfile(path) and os.stat(path).st_nlink > 1:
        raise RuntimeError(f"Refusing hard link at {path!r}")
    real = os.path.realpath(path)
    base = os.path.realpath(allowed_base)
    if not real.startswith(base + os.sep):
        raise RuntimeError(f"Path {real!r} outside allowed base {base!r}")
    