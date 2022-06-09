# from django.core.cache import cache
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.utils import timezone
#
# from payment.models import PayCategory
#
#
# @receiver([post_save, post_delete], sender=PayCategory)  # TODO
# def change_api_updated_at(sender, instance, *args, **kwargs):
#     # 数据表数据发生变化时(保存、删除), 缓存最新更新时间 https://chibisov.github.io/drf-extensions/docs/#custom-key-bit
#     sender_meta = sender._meta
#     app_label = sender_meta.app_label
#     model_name = sender_meta.model_name
#     cache.set(f'{app_label}:{model_name}:post_updated_at', timezone.now())  # 更新drf_extensions相关缓存
# instance.cache_invalidate()  # 清除redis中的缓存，已在save方法中调用
