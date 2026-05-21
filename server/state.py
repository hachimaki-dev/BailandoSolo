"""
Bailando Solo — Shared mutable state with thread safety.
"""

import threading


# Thread-safe download progress tracking.
# Keys are video IDs, values are dicts with status/percent/filename/speed/eta.
_download_status = {}
_status_lock = threading.Lock()


def get_download_status():
    """Return a snapshot of current download status (thread-safe)."""
    with _status_lock:
        return dict(_download_status)


def update_download_status(video_id: str, status_data: dict):
    """Update status for a specific download (thread-safe)."""
    with _status_lock:
        _download_status[video_id] = status_data
