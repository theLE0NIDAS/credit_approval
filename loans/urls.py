from django.urls import path
from .views import CheckEligibility, CreateLoan, ViewLoan, ViewLoans, IngestData

urlpatterns = [
    path('ingest/', IngestData.as_view(), name='ingest_data'),
    path('check-eligibility/', CheckEligibility.as_view(), name='check_eligibility'),
    path('create-loan/', CreateLoan.as_view(), name='create_loan'),
    path('view-loan/<str:loan_id>/', ViewLoan.as_view(), name='view_loan'),
    path('view-loans/<str:customer_id>/', ViewLoans.as_view(), name='view_loans'),
]
