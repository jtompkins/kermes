import functools
import time


class retry:
    def __init__(self, max_retries=3, fallback_secs=3, exponential=True):
        self.max_retries = max_retries
        self.fallback_secs = fallback_secs
        self.exponential = exponential

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            err_result = None
            retries = 0
            while retries < self.max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    err_result = err
                    retries += 1
                    if self.exponential:
                        time.sleep(retries * self.fallback_secs)
                    else:
                        time.sleep(self.fallback_secs)

            raise err_result

        return wrapper
