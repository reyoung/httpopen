from typing import Optional

import requests
import collections

__all__ = ["http_open"]


class SyncHTTPReader:
    def __init__(self, url: str, chunk_size: int = 4096):
        s = requests.Session()
        self._rsp = s.get(url, stream=True)
        if self._rsp.status_code != 200:
            self._rsp.close()
            raise ValueError(f"Failed to download {url}")
        self._iter = self._rsp.iter_content(chunk_size=chunk_size)
        self._buf = collections.deque()
        self._chunk_size = chunk_size

    def _buf_size(self) -> int:
        return sum((len(item) for item in self._buf))

    def _fetch_at_least(self, size: int):
        if self._iter is None:
            return
        try:
            buf = next(self._iter)
        except StopIteration:
            self._iter = None
            return

        self._buf.append(buf)
        if len(buf) < size:
            self._fetch_at_least(size - len(buf))

    def _yield_at_least(self, size: int):
        if size == 0:
            return
        if len(self._buf) == 0:
            return
        buf = self._buf[0]
        if len(buf) <= size:
            yield buf
            self._buf.popleft()
            yield from self._yield_at_least(size - len(buf))
            return
        yield buf[:size]
        self._buf[0] = buf[size:]

    def _pop(self, size: int) -> bytes:
        if len(self._buf) == 0:
            return b""

        return b"".join(self._yield_at_least(size))

    def _read_all(self) -> bytes:
        if self._iter is not None:
            for buf in self._iter:
                self._buf.append(buf)
            self._iter = None
        return b"".join(self._buf)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def read(self, size: int = -1) -> Optional[bytes]:
        if size < 0:
            self._read_all()

        buf_size = self._buf_size()
        if buf_size < size:
            self._fetch_at_least(size - buf_size)

        return self._pop(size)

    def close(self):
        if self._rsp is None:
            return
        self._rsp.close()
        self._rsp = None


def http_open(url: str, chunk_size: int = 4096) -> SyncHTTPReader:
    return SyncHTTPReader(url, chunk_size=chunk_size)
