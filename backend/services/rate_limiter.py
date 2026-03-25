from __future__ import annotations

import os
import time
from collections import defaultdict, deque

from fastapi import HTTPException


class UploadRateLimiter:
    def __init__(self) -> None:
        self.window_seconds = int(os.getenv("UPLOAD_RATE_WINDOW_SECONDS", "60"))
        self.max_requests = int(os.getenv("UPLOAD_RATE_MAX_REQUESTS", "8"))
        self.max_large_requests = int(os.getenv("UPLOAD_RATE_MAX_LARGE_REQUESTS", "3"))
        self.large_upload_bytes = int(os.getenv("UPLOAD_RATE_LARGE_UPLOAD_BYTES", str(512 * 1024)))
        self.max_single_upload_bytes = int(os.getenv("UPLOAD_MAX_SINGLE_BYTES", str(5 * 1024 * 1024)))
        self.max_total_window_bytes = int(os.getenv("UPLOAD_MAX_WINDOW_BYTES", str(20 * 1024 * 1024)))
        self._events: dict[str, deque[tuple[float, int]]] = defaultdict(deque)

    def check(self, client_id: str, upload_size_bytes: int) -> None:
        if upload_size_bytes > self.max_single_upload_bytes:
            raise HTTPException(status_code=413, detail="Upload exceeds the maximum allowed size.")

        now = time.time()
        events = self._events[client_id]
        while events and now - events[0][0] > self.window_seconds:
            events.popleft()

        total_bytes = sum(size for _, size in events)
        large_count = sum(1 for _, size in events if size >= self.large_upload_bytes)
        is_large = upload_size_bytes >= self.large_upload_bytes

        if len(events) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Too many upload requests in the current time window.")
        if is_large and large_count >= self.max_large_requests:
            raise HTTPException(status_code=429, detail="Too many large log uploads in the current time window.")
        if total_bytes + upload_size_bytes > self.max_total_window_bytes:
            raise HTTPException(status_code=429, detail="Upload volume exceeds the current rate limit budget.")

        events.append((now, upload_size_bytes))
