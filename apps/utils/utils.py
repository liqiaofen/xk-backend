from collections import defaultdict


def get_queryset_default_dict(queryset, key):
    # 返回 {'xx':[obj1, obj2], 'yy':[...]}
    result = defaultdict(list)
    for obj in queryset:
        result[str(obj[key])].append(obj)
    result.default_factory = None
    return result
