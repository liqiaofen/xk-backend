import re

from django.conf import settings
from django.db import connection
from django.shortcuts import redirect
from django.urls import reverse


class BackendRbacMiddleware:
    """
    后端管理系统用户权限信息校验
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # 配置和初始化

    def __call__(self, request):
        # 在这里编写视图和后面的中间件被调用之前需要执行的代码
        # 这里其实就是旧的process_request()方法的代码

        # 1. 获取当前用户请求的URL
        # 2. 获取当前用户在session中保存的权限列表 ['/customer/list/','/customer/list/(?P<cid>\\d+)/']
        # 3. 权限信息匹配
        response = self.get_response(request)
        current_url = request.path_info

        if current_url.startswith('/backend/'):  # 后端地址
            # 未登录返回登录页面
            if not request.user.is_authenticated:
                # 白名单
                for valid_url in settings.VALID_URL_LIST:
                    if re.match('^%s$' % valid_url, current_url):
                        return response
                return redirect(reverse('backend-login'))

        # 面包屑
        # breadcrumb = [
        #     {'name': '首页', 'url': '/console/dashboard/'}  # 只有后台系统才需要面包屑。
        # ]

        # 此处判断： 如果是 /logout/ /index/ 这种登录成功，但是不需要校验权限的页面
        # for url in settings.NO_PERMISSION_LIST:
        #     if re.match(url, current_url):
        #         # request.current_selected = 0  # 默认展开菜单
        #         # request.breadcrumb = breadcrumb
        #         # 需要登录当时无需权限的页面直接通过
        #         response = self.get_response(request)
        #         return response

        # if not permission_dict:  # 0权限，没有登录，这样是不是可以不用LoginRequiredMixin了？
        #     return redirect(reverse('login'))

        # 在这里编写视图调用后需要执行的代码
        # 这里其实就是旧的process_response()方法的代码
        return response


class SQLPrintingMiddleware:
    def __init__(self, get_response):
        print('SQL Printing')
        self.get_response = get_response

    def __call__(self, request):
        print('SQL Queries for:', request.path_info)
        response = self.get_response(request)
        total_time = 0.0
        num = 0
        for query in connection.queries:
            print('exec time:', query['time'])
            print('sql:', query['sql'])
            print('-' * 20)
            total_time += float(query['time'])
            num += 1
        print('Total Time:', str(total_time))
        print('Total SQL:', num)
        return response
