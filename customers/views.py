from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tasks import ingest_customer_data
from .models import Customer
from .serializers import RegisterCustomerSerializer, CustomerResponseSerializer
from loans.models import Loan
import math

class IngestData(APIView):
    def post(self, request):
        customer_file = request.FILES.get('customer_file')

        customer_file_path = f"tmp/{customer_file.name}"

        with open(customer_file_path, 'wb') as f:
            for chunk in customer_file.chunks():
                f.write(chunk)

        ingest_customer_data.delay(customer_file_path)

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

