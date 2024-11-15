from django.db import models
from customers.models import Customer
from datetime import date

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_id = models.AutoField(max_length=20, unique=True, primary_key=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField( auto_now_add=True)
    end_date = models.DateField(auto_now_add=True )

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer}"
