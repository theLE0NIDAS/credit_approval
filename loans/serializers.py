from rest_framework import serializers
from .models import Loan
from customers.models import Customer

class CreateLoanRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['customer', 'loan_amount', 'interest_rate', 'tenure']

class CreateLoanResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['customer', 'loan_amount', 'interest_rate', 'tenure', 'monthly_installment']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age']

class LoanIDResponseSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']

class LoanCIDResponseSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']
    
    def get_repayments_left(self, obj):
        return obj.tenure - obj.emis_paid_on_time

class EligibilityRequestSerializer(serializers.Serializer):
    class Meta:
        model = Loan
        fields = ['customer', 'loan_amount', 'interest_rate', 'tenure']

class EligibilityResponseSerializer(serializers.Serializer):
    approval = serializers.BooleanField()
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    customer_id = serializers.IntegerField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
