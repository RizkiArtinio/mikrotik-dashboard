import os
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def router_backup_dir(base_dir: str, router_id: int) -> Path:
    return ensure_dir(Path(base_dir) / str(router_id))


def file_size_bytes(path: str | Path) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0
