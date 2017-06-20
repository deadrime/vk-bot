import time


def rate_limited(min_interval):
    def decorate(func):
        last_time_called = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.time() - last_time_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kargs)
            last_time_called[0] = time.time()
            return ret
        return rate_limited_function
    return decorate