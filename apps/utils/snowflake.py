import datetime
import time

from django.conf import settings

# https://github.com/falcondai/python-snowflake
# twitter's snowflake parameters
twepoch = 1609430400000  # 元年时间戳2021-01-01(+8)
datacenter_id_bits = 5
worker_id_bits = 5
sequence_id_bits = 12
max_datacenter_id = 1 << datacenter_id_bits
max_worker_id = 1 << worker_id_bits
max_sequence_id = 1 << sequence_id_bits
max_timestamp = 1 << (53 - datacenter_id_bits - worker_id_bits - sequence_id_bits)

DATACENTER_ID = settings.DATACENTER_ID
WORKER_ID = settings.WORKER_ID


def make_snowflake(sequence_id=0):
    """generate a twitter-snowflake id, based on
    https://github.com/twitter/snowflake/blob/master/src/main/scala/com/twitter/service/snowflake/IdWorker.scala
    :param: timestamp_ms time since UNIX epoch in milliseconds"""
    timestamp = time.time() * 1000
    sid = ((int(timestamp) - twepoch) % max_timestamp) << datacenter_id_bits << worker_id_bits << sequence_id_bits
    sid += (DATACENTER_ID % max_datacenter_id) << worker_id_bits << sequence_id_bits
    sid += (WORKER_ID % max_worker_id) << sequence_id_bits
    sid += sequence_id % max_sequence_id
    return sid


def melt(snowflake_id, twepoch=twepoch):
    """inversely transform a snowflake id back to its parts."""
    sequence_id = snowflake_id & (max_sequence_id - 1)
    worker_id = (snowflake_id >> sequence_id_bits) & (max_worker_id - 1)
    datacenter_id = (snowflake_id >> sequence_id_bits >> worker_id_bits) & (max_datacenter_id - 1)
    timestamp_ms = snowflake_id >> sequence_id_bits >> worker_id_bits >> datacenter_id_bits
    timestamp_ms += twepoch

    return timestamp_ms, int(datacenter_id), int(worker_id), int(sequence_id)


def local_datetime(timestamp_ms):
    """convert millisecond timestamp to local datetime object."""
    return datetime.datetime.fromtimestamp(timestamp_ms / 1000.)
