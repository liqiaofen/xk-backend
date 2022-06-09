from django.views.generic import ListView

from core.backend_views import BackendListBaseView
from expense.models import PayCategory, Expense
from utils.paginator import PaginationMixin
from utils.utils import get_queryset_default_dict


class PayCategoryView(PaginationMixin, ListView):
    model = PayCategory
    context_object_name = "paycategories"
    template_name = "backend/expense/pay_category.html"


class ExpenseView(PaginationMixin, BackendListBaseView):
    model = Expense
    context_object_name = "expenses"
    template_name = "backend/expense/expense.html"
    page_name = '账单列表'

    def get_queryset(self):
        queryset = super(ExpenseView, self).get_queryset()
        return queryset.select_related('created_by')

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['pay_categories'] = get_queryset_default_dict(
            PayCategory.objects.filter().order_by('pay_type', 'sort').values(), 'pay_type')

        kwargs['data'] = {'a': [[1, 2]], 'b': [[3, 4]], 'c': [[5, 6]]}

        # kwargs['ali_icons'] = json.loads(requests.get(settings.ALICDN_ICONFONT).text.replace('\\', '/'))
        kwargs['ali_icons'] = {
            "id": "3279671",
            "name": "small-love",
            "font_family": "iconfont",
            "css_prefix_text": "icon-",
            "description": "",
            "glyphs": [
                {
                    "icon_id": "25164538",
                    "name": "酒店预订",
                    "font_class": "jiudianyuding",
                    "unicode": "fd6d",
                    "unicode_decimal": 64877
                },
                {
                    "icon_id": "25164552",
                    "name": "培训",
                    "font_class": "peixun",
                    "unicode": "fd6e",
                    "unicode_decimal": 64878
                },
                {
                    "icon_id": "25164566",
                    "name": "家政服务",
                    "font_class": "jiazhengfuwu",
                    "unicode": "fd6f",
                    "unicode_decimal": 64879
                },
                {
                    "icon_id": "25164572",
                    "name": "装饰",
                    "font_class": "zhuangshi",
                    "unicode": "fd70",
                    "unicode_decimal": 64880
                },
                {
                    "icon_id": "25164574",
                    "name": "二手回收",
                    "font_class": "ershouhuishou",
                    "unicode": "fd71",
                    "unicode_decimal": 64881
                },
                {
                    "icon_id": "25164578",
                    "name": "二手车",
                    "font_class": "ershouche",
                    "unicode": "fd72",
                    "unicode_decimal": 64882
                },
                {
                    "icon_id": "25164591",
                    "name": "蔬果供求",
                    "font_class": "shuguogongqiu",
                    "unicode": "fd73",
                    "unicode_decimal": 64883
                }]}
        return super(ExpenseView, self).get_context_data(object_list=object_list, **kwargs)
