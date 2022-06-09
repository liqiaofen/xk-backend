import datetime
import hashlib
import os
from uuid import uuid4

from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text


def tokey(*args):
    def _encode(value, charset="utf-8", errors="ignore"):
        if isinstance(value, bytes):
            return value
        return value.encode(charset, errors)

    salt = "||".join([force_text(arg) for arg in args])
    hash_ = hashlib.md5(_encode(salt))
    return hash_.hexdigest()


@deconstructible
class FilePathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]
        now = str(datetime.datetime.now())

        if hasattr(instance, "created_by") and instance.created_by.username:
            key = tokey(instance.created_by.username, filename, now)
            filename = "{}.{}".format(key, ext)
        else:
            key = tokey(uuid4().hex, ext, now)
            filename = "{}.{}".format(key, ext)
        # return the whole relative path to the file
        return os.path.join(self.path, filename)
