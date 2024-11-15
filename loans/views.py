from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tasks import ingest_loan_data
from .models import Loan
from .serializers import CreateLoanRequestSerializer, CreateLoanResponseSerializer, LoanIDResponseSerializer, LoanCIDResponseSerializer, CustomerSerializer, EligibilityRequestSerializer, EligibilityResponseSerializer
from customers.models import Customer

class IngestData(APIView):
    def post(self, request):
        loan_file = request.FILES.get('loan_file')

        loan_file_path = f"tmp/{loan_file.name}"

        with open(loan_file_path, 'wb') as f:
            for chunk in loan_file.chunks():
                f.write(chunk)

        ingest_loan_data.delay(loan_file_path)

        return Response({"message": "Data ingestion started. This may take a while."}, status=status.HTTP_200_OK)

class CheckEligibility(APIView):
    def post(self, request):

        request_serializer = EligibilityRequestSerializer(data=request.data)

        if not request_serializer.is_valid():
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount'))
        interest_rate = float(request.data.get('interest_rate'))
        tenure = int(request.data.get('tenure'))

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
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def calculate_credit_score(self, customer):
        loans = Loan.objects.filter(customer=customer)
        current_loans_sum = sum(loan.loan_amount for loan in loans)
        
        if current_loans_sum > customer.approved_limit:
            return 0
        
        total_emi = sum(loan.monthly_installment for loan in loans)
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
                }, status=status.HTTP_200_OK)

            loan_data = {
                "customer": customer.customer_id,
                "loan_amount": loan_amount,
                "interest_rate": eligibility_data["corrected_interest_rate"],
                "monthly_installment": eligibility_data["monthly_installment"],
                "tenure": tenure
            }

            serializer = CreateLoanResponseSerializer(data=loan_data)
            serializer.is_valid(raise_exception=True)  
            loan = serializer.save()

            return Response({
                    "loan_id": loan.loan_id,
                    "customer_id": customer_id,
                    "loan_approved": True,
                    "message": "Loan approved.",
                    "monthly_installment": loan.monthly_installment,
                }, status=status.HTTP_201_CREATED)
        
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ViewLoans(APIView):
    def get(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            loans = Loan.objects.filter(customer=customer)
            loans_data = LoanCIDResponseSerializer(loans, many=True).data
                
            return Response(loans_data, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
