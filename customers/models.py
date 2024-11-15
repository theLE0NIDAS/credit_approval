from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(max_length=20, unique=True, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(max_length=3)
    phone_number = models.CharField(max_length=10)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.customer_id} {self.first_name} {self.last_name}"
