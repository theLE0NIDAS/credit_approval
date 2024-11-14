from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Loan
from .serializers import LoanSerializer
from customers.models import Customer
from customers.views import CheckEligibility

class CreateLoan(APIView):
    def post(self, request, *args, **kwargs):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount'))
        interest_rate = float(request.data.get('interest_rate'))
        tenure = int(request.data.get('tenure'))

        try:
            customer = Customer.objects.get(customer_id=customer_id)
            
            eligibility_check = CheckEligibility()
            eligibility_data = eligibility_check.post(request).data
            
            if not eligibility_data['approval']:
                return Response({
                    "loan_id": None,
                    "customer_id": customer_id,
                    "loan_approved": False,
                    "message": "Loan not approved due to eligibility criteria.",
                    "monthly_installment": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            
            loan_data = {
                "customer": customer.id,
                "loan_amount": loan_amount,
                "interest_rate": eligibility_data["corrected_interest_rate"],
                "tenure": tenure,
                "monthly_repayment": eligibility_data["monthly_installment"]
            }
            serializer = LoanSerializer(data=loan_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

class ViewLoan(APIView):
    def get(self, request, *args, **kwargs):
        loan_id = kwargs.get('loan_id')
        try:
            loan = Loan.objects.get(loan_id=loan_id)
            loan_data = LoanSerializer(loan).data
            
            customer_data = {
                "id": loan.customer.customer_id,
                "first_name": loan.customer.first_name,
                "last_name": loan.customer.last_name,
                "phone_number": loan.customer.phone_number,
                "age": loan.customer.age,
            }
            
            response_data = {**loan_data, "customer": customer_data}
            return Response(response_data)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

class ViewLoans(APIView):
    def get(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            loans = Loan.objects.filter(customer=customer)
            
            loans_data = [
                {
                    **LoanSerializer(loan).data,
                    "repayments_left": loan.tenure - loan.emis_paid_on_time.count(True)
                }
                for loan in loans
            ]
            
            return Response(loans_data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
