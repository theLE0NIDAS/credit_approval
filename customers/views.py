from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tasks import ingest_customer_data
from .models import Customer
from .serializers import RegisterCustomerSerializer, CustomerResponseSerializer
from loans.models import Loan
import math

class IngestData(APIView):
    def post(self, request, *args, **kwargs):
        customer_file_path = request.data.get('customer_file_path')

        if not customer_file_path:
            return Response({"error": "File paths are required."}, status=status.HTTP_400_BAD_REQUEST)

        ingest_customer_data(customer_file_path)

        return Response({"message": "Data ingestion started. This may take a while."}, status=status.HTTP_200_OK)

class RegisterCustomer(APIView):
    def post(self, request):
        input_serializer = RegisterCustomerSerializer(data=request.data)

        if input_serializer.is_valid():
            customer = input_serializer.save()
            customer.approved_limit = round(36 * float(customer.monthly_salary), -5)
            customer.save()

            output_serializer = CustomerResponseSerializer(customer)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

