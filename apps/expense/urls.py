from django.urls import path

from expense.views import ExpenseView, PayCategoryView

app_name = 'expense'

urlpatterns = [
    path('', ExpenseView.as_view(), name='expense'),
    path('category/', PayCategoryView.as_view(), name='expense-category'),
]
