import functools
import time


def retry(max_attempts=3, fallback_secs=3, exponential=True, exceptions=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            err_result = None
            retries = 0
            while retries <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    err_result = err

                    if exceptions is not None and type(err) not in exceptions:
                        break

                    retries += 1

                    time.sleep(
                        fallback_secs ** retries if exponential else fallback_secs
                    )

            raise err_result

        return wrapper

    return decorator
