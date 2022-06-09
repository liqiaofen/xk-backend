from django.core.cache import cache
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.cache.mixins import BaseCacheResponseMixin
from rest_framework_extensions.key_constructor.bits import KeyBitBase, ListSqlQueryKeyBit, QueryParamsKeyBit
from rest_framework_extensions.key_constructor.constructors import DefaultKeyConstructor


class ReadWriteSerializerMixin(object):
    """
    # https://www.revsys.com/tidbits/using-different-read-and-write-serializers-django-rest-framework/
    class MyModelViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
        queryset = MyModel.objects.all()
        read_serializer_class = ModelReadSerializer
        write_serializer_class = ModelWriteSerializer
    """
    read_serializer_class = None
    write_serializer_class = None

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return self.get_write_serializer_class()
        return self.read_serializer_class

    def get_read_serializer_class(self):
        assert self.read_serializer_class is not None, (
                "`%s` 应该包含 `read_serializer_class` 属性 或者重写 `get_read_serializer_class()`方法。 " % self.__class__.__name__
        )
        return self.read_serializer_class

    def get_write_serializer_class(self):
        assert self.write_serializer_class is not None, (
                "`%s` 应该包含 `write_serializer_class` 属性 或者重写 `get_write_serializer_class()`方法。 " % self.__class__.__name__
        )
        return self.write_serializer_class


class MultiSelectionMixin:
    def multi_selection(self, request, limit: int = 0):
        """以后可供批量删除，生成分单等多选按钮操作，支持单页多选和跨页多选
        如果view没有继承这个mixin，只能重写相关代码"""
        # 当调用这个方法是，默认是勾选了跨页全选，可以获取符合条件的所有对象。
        # 也就是说，前端的跨页全选按钮，只是一个样子，展现出checkbox被勾选了，最后并没有提供实际的url参数
        # 当然，前端也做了一些限定。没有勾选跨页全选按钮就不能进行相关请求。
        # 当然，还有一种方法，前端勾选了跨页全选，在实际调用比如生成分单，批量删除时，先调用某个接口，把这些所有id都获取回去，
        # 然后再次请求，把id放入列表中，这边根据id再一一筛选。缺点是要多次操作数据库
        # 这个方法是原 get_objects 里面写好的
        qs = self.filter_queryset(self.get_queryset())
        # 前端request参数名如果用data而不是params，比如 batchGenerateIncome(data)，那么django request的query_params 里面就获取不到数据，
        # 数据就在request.data里面,并且data是一个字典，不能用getlist方法
        # 还有一个区别就是request.query_params.getlist('id')获取到的数据是字符串的列表，而 request.data.get('id') 获取到的是数字的列表。
        checked_ids = request.query_params.getlist(
            'id') or request.data.get('id')
        if checked_ids:
            if 0 < limit < len(checked_ids):
                raise ValidationError(f'最多支持操作{limit}条数据')
            qs = qs.filter(id__in=checked_ids)
        if not qs.exists():  # 校验下queryset不能为空
            raise ValidationError('未选择任何有效数据')
        return qs


class BaseAPIViewMixin(MultiSelectionMixin):
    def get_queryset(self):
        queryset = super(BaseAPIViewMixin, self).get_queryset()
        # 下面的方法是为了连表查询，使用select_related等
        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, 'get_related_queries'):
            queryset = serializer_class.get_related_queries(queryset)
        return queryset

    def paginate_queryset(self, queryset):
        # 方便前端一些下拉菜单，一次获取所有数据，不用分页
        if self.request.query_params.get('_paginator') == "none":
            return None
        else:
            return super().paginate_queryset(queryset)

    def get_serializer_context(self):
        context = super(BaseAPIViewMixin, self).get_serializer_context()
        context['action'] = self.action  #
        return context


class LoverAPIViewMixin(BaseAPIViewMixin):
    def get_queryset(self):
        queryset = super(LoverAPIViewMixin, self).get_queryset()
        queryset = queryset.filter(created_by__in=[self.request.user, self.request.user.lover])
        return queryset


# drf-extensions
class UpdatedAtKeyBit(KeyBitBase):
    init_key = None

    def get_data(self, **kwargs):
        key = self.init_key
        if key is None:
            # 默认为'country:post_updated_at'
            model_meta = kwargs['view_instance'].queryset.model._meta
            app_label = model_meta.app_label
            model_name = model_meta.model_name
            key = f'{app_label}:{model_name}:post_updated_at'
        value = cache.get(key, None)
        if not value:
            value = timezone.now()
            cache.set(key, value=value)
        return str(value)


class PostListKeyConstructor(DefaultKeyConstructor):
    list_sql = ListSqlQueryKeyBit()
    query_params = QueryParamsKeyBit()  # 查询参数， 包含了分页查询
    updated_at = UpdatedAtKeyBit()  # 数据是否更新变化


class ListCacheResponseMixin(BaseCacheResponseMixin):
    """缓存list数据，提供了对传入动态字段参数的支持"""

    @cache_response(key_func=PostListKeyConstructor(), timeout=60 * 60 * 12)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RetrievePatchOnlyAPIView(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class UpdateDestoryAPIView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveCreateDestroyAPIView(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                                   GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveCreateAPIView(mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericAPIView, ):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BulkDataPostAPIView(GenericAPIView):
    serializer_class = None
    data_key = None

    def get_request_data(self):
        request_data = self.request.data
        return request_data if isinstance(request_data, list) else [request_data]

    def get_extra_context(self):
        return {}

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(self.get_extra_context())
        return context

    def process_serializer(self, serializers):
        items = []
        for serializer in serializers:
            serializer.save()
            items.append(serializer.validated_data)
        return items

    def post(self, request, *args, **kwargs):
        errors = []
        serializers = []

        post_data = self.get_request_data()
        for data in post_data:
            serializer = self.get_serializer(data=data,
                                             context=self.get_serializer_context()
                                             )
            if serializer.is_valid(raise_exception=False):
                serializers.append(serializer)
            else:
                data_value = data.get(self.data_key, None)
                if data_value:
                    error_dict = {data_value: serializer.errors}
                else:
                    error_dict = serializer.errors
                errors.append(error_dict)
        if len(errors) > 0:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return_data = self.process_serializer(serializers)
        return Response(return_data, status=status.HTTP_200_OK)
