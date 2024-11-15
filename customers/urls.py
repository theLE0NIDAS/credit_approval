from django.urls import path
from .views import RegisterCustomer, IngestData

urlpatterns = [
    path('register/', RegisterCustomer.as_view(), name='register_customer'),
    path('ingest/', IngestData.as_view(), name='ingest_data')
]
