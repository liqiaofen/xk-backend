import time
from functools import wraps

from django.db import reset_queries, connection


def debugger_queries(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('func:', func.__name__)
        reset_queries()

        start = time.time()
        start_queries = len(connection.queries)

        result = func(*args, **kwargs)

        end = time.time()
        end_queries = len(connection.queries)
        # print(connection.queries)
        print('queires', end_queries - start_queries)
        print('Total time:%.2fs' % (end - start))

        return result

    return wrapper
