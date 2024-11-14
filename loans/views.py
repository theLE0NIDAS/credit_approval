from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Loan
from .serializers import CreateLoanRequestSerializer, CreateLoanResponseSerializer, LoanIDResponseSerializer, LoanCIDResponseSerializer, CustomerSerializer, EligibilityRequestSerializer, EligibilityResponseSerializer
from customers.models import Customer

class CheckEligibility(APIView):
    def post(self, request):
        request_serializer = EligibilityRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        customer_id = request_serializer.validated_data['customer_id']
        loan_amount = float(request_serializer.validated_data['loan_amount'])
        interest_rate = float(request_serializer.validated_data['interest_rate'])
        tenure = int(request_serializer.validated_data['tenure'])
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            
            credit_score = self.calculate_credit_score(customer)
            
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

            monthly_installment = (
                self.calculate_monthly_installment(loan_amount, final_interest_rate, tenure)
                if approval else None
            )
            
            response_data = {
                "customer_id": customer.customer_id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": final_interest_rate,
                "tenure": tenure,
                "monthly_installment": monthly_installment,
            }
            response_serializer = EligibilityResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    def calculate_credit_score(self, customer):
        loans = Loan.objects.filter(customer=customer)
        current_loans_sum = sum(loan.loan_amount for loan in loans)
        
        if current_loans_sum > customer.approved_limit:
            return 0
        
        total_emi = sum(loan.monthly_repayment for loan in loans)
        if total_emi > (0.5 * float(customer.monthly_salary)):
            return 0

        credit_score = min(100, max(0, 50 + len(loans) * 10))
        
        return credit_score
    
    def calculate_monthly_installment(self, loan_amount, interest_rate, tenure):
        monthly_interest_rate = interest_rate / (12 * 100)
        emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure / ((1 + monthly_interest_rate) ** tenure - 1)
        return round(emi, 2)


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
                "monthly_installment": eligibility_data["monthly_installment"]
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
            
            loan_data = LoanIDResponseSerializer(loan).data
            
            customer_data = CustomerSerializer(loan.customer).data
            
            loan_data["customer"] = customer_data
            
            return Response(loan_data, status=status.HTTP_200_OK)
        
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

class ViewLoans(APIView):
    def get(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            
            loans = Loan.objects.filter(customer=customer)
            
            loans_data = LoanCIDResponseSerializer(loans, many=True).data
            
            for loan, loan_data in zip(loans, loans_data):
                loan_data["repayments_left"] = loan.tenure - loan.emis_paid_on_time.count(True)
                
            return Response(loans_data, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
