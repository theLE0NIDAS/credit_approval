from django.urls import path
from .views import CreateLoan, ViewLoan, ViewLoans

urlpatterns = [
    path('create-loan/', CreateLoan.as_view(), name='create_loan'),
    path('view-loan/<str:loan_id>/', ViewLoan.as_view(), name='view_loan'),
    path('view-loans/<str:customer_id>/', ViewLoans.as_view(), name='view_loans'),
]
