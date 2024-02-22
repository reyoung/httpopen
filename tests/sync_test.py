import unittest
from httpopen.sync import http_open


class TestHTTPOpen(unittest.TestCase):
    def test_http_open_read_all(self):
        with http_open("https://httpbin.org/get") as f:
            self.assertNotEquals(len(f.read()), 0)

    def test_http_open_read_chunk(self):
        with http_open("https://httpbin.org/get") as f:
            while True:
                chunk = f.read(10)
                if not chunk:
                    break
                print(chunk)
                self.assertNotEquals(len(chunk), 0)
