import json
import logging
from collections import OrderedDict

from django.core.paginator import InvalidPage
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

request_err_log = logging.getLogger('request_err')


class BaseResponse:
    def __init__(self):
        self.code = 20000
        self.data = None
        self.errors = None

    @property
    def dict(self):
        # print(self.__dict__)
        return self.__dict__


class FitJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        """
        如果使用这个render，
        普通的response将会被包装成：
            {"code":200,"data":"X","msg":"X"}
        使用方法：
            - 全局
                REST_FRAMEWORK = {
                'DEFAULT_RENDERER_CLASSES': ('utils.response.FitJSONRenderer', ),
                }
            - 局部
                class UserCountView(APIView):
                    renderer_classes = [FitJSONRenderer]
        """
        response_body = BaseResponse()
        response = renderer_context.get('response')
        response_body.code = response.status_code
        if response_body.code >= 400:
            request_err_log.error(json.dumps(data, ensure_ascii=False))
            response_body.errors = data['detail'] if 'detail' in data else data
        else:
            response_body.data = data
        return super(FitJSONRenderer, self).render(response_body.dict, accepted_media_type, renderer_context)


class JsonBaseResponse(JsonResponse):

    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True,
                 json_dumps_params=None, **kwargs):
        if json_dumps_params is None:
            json_dumps_params = {'ensure_ascii': False}
        super(JsonBaseResponse, self).__init__(data, encoder=encoder, safe=True,
                                               json_dumps_params=json_dumps_params, **kwargs)


class CommonPagination(PageNumberPagination):
    '''
    分页设置
    '''
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):

        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.page.next_page_number() if self.page.has_next() else 1),
            ('previous', self.page.previous_page_number() if self.page.has_previous() else 1),
            ('has_previous', self.page.has_previous()),
            ('has_next', self.page.has_next()),
            ('current', self.page.number),
            ('results', data)
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        """
        重写分页查询，当页数无效时，查找最后一页的数据
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            # 无效页数，返回到最后一页
            self.page = paginator.page(paginator.num_pages)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
