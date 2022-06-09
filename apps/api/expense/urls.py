from django.urls import path, include
from rest_framework_nested import routers

from api.expense.views import PayCategoryApiViewSet, ExpenseApiViewSet

app_name = 'api-expense'

router = routers.SimpleRouter()

router.register('categories', PayCategoryApiViewSet, basename="expense-category")
router.register('', ExpenseApiViewSet, basename="expense")

urlpatterns = [
    path('', include(router.urls)),
]
