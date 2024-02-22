# HTTPOpen

open a http url as a local file.

## Usage

```python
from httpopen import http_open

with http_open("https://httpbin.org/get") as f:
    print(f.read())
```
