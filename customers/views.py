from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer
from .serializers import CustomerSerializer
from loans.models import Loan
import math

class RegisterCustomer(APIView):
    def post(self, request):
        data = request.data
        monthly_salary = data.get("monthly_salary")
        
        approved_limit = round(36 * float(monthly_salary), -5)
        data['approved_limit'] = approved_limit

        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckEligibility(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount'))
        interest_rate = float(request.data.get('interest_rate'))
        tenure = int(request.data.get('tenure'))
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            
            credit_score, message = self.calculate_credit_score(customer)
            
            if credit_score > 50:
                approval = True
                final_interest_rate = interest_rate
            elif 30 < credit_score <= 50:
                approval = True
                final_interest_rate = max(12.0, interest_rate)
            elif 10 < credit_score <= 30:
                approval = True
                final_interest_rate = max(16.0, interest_rate)
            else:
                approval = False
                final_interest_rate = None

            if approval:
                monthly_installment = self.calculate_monthly_installment(loan_amount, final_interest_rate, tenure)
            else:
                monthly_installment = None
            
            response_data = {
                "customer_id": customer.customer_id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": final_interest_rate,
                "tenure": tenure,
                "monthly_installment": monthly_installment,
                "credit_score": credit_score,
                "message": message
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    def calculate_credit_score(self, customer):
        loans = Loan.objects.filter(customer=customer)
        current_loans_sum = sum(loan.loan_amount for loan in loans)
        
        if current_loans_sum > customer.approved_limit:
            return 0, "Current loans exceed approved limit."

        credit_score = min(100, max(0, 50 + len(loans) * 10))
        
        return credit_score, "Calculated credit score based on customer loan history."
    
    def calculate_monthly_installment(self, loan_amount, interest_rate, tenure):
        monthly_interest_rate = interest_rate / (12 * 100)
        emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure / ((1 + monthly_interest_rate) ** tenure - 1)
        return round(emi, 2)
