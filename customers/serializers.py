from rest_framework import serializers
from .models import Customer

class RegisterCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_salary', 'phone_number']

class CustomerResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    approved_limit = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_salary', 'approved_limit', 'phone_number']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

