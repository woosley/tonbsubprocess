# nbsubprocess

a non-blocking subprocess lib for tornado

## Usage

```python
from nbsubprocess import NonBlockingSubprocess
from tornado.gen import Task, coroutine

class MyHandler(RequestHandler):
    @corotine
    def get(self):
        cmd = "echo hello && sleep 1 && echo goodbye"
        res = yield Task(NonBlockingSubprocess(cmd).loop)
        return_code = res.pipe.return_code
        output = res.output
```

## Test
nose test.py
