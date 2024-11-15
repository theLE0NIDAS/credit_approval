import pandas as pd
from background_task import background
from .models import Loan
from customers.models import Customer
from django.core.exceptions import ValidationError

@background(schedule=0)
def ingest_loan_data(file_path):
    try:
        data = pd.read_excel(file_path)
        for _, row in data.iterrows():
            customer = Customer.objects.get(customer_id=row['Customer ID'])
            Loan.objects.update_or_create(
                loan_id=row['Loan ID'],
                defaults={
                    "customer": customer,
                    "loan_amount": row['Loan Amount'],
                    "interest_rate": row['Interest Rate'],
                    "tenure": row['Tenure'],
                    "monthly_installment": row['Monthly payment'],
                    "emis_paid_on_time": row['EMIs paid on Time'],
                    "start_date": row['Date of Approval'],
                    "end_date": row['End Date'],
                }
            )
        print("Loan data ingested successfully.")
    except Exception as e:
        print(f"Error ingesting loan data: {e}")
        
# def ingest_loan_data(file_path):
#     try:
#         df = pd.read_excel(file_path)

#         for _, row in df.iterrows():
#             loan_id = row['Loan ID']
#             customer_id = row['Customer ID']
#             loan_amount = row['Loan Amount']
#             interest_rate = row['Interest Rate']
#             tenure = row['Tenure']
#             monthly_repayment = row['Monthly payment']
#             emis_paid_on_time = row['EMIs paid on Time']
#             start_date = row['Date of Approval']
#             end_date = row['End Date']

#             try:
#                 customer = Customer.objects.get(customer_id=customer_id)
#             except Customer.DoesNotExist:
#                 print(f"Customer with ID {customer_id} does not exist.")
#                 continue

#             loan = Loan(
#                 loan_id=loan_id,
#                 customer=customer,
#                 loan_amount=loan_amount,
#                 interest_rate=interest_rate,
#                 tenure=tenure,
#                 monthly_repayment=monthly_repayment,
#                 emis_paid_on_time=emis_paid_on_time,
#                 start_date=start_date,
#                 end_date=end_date
#             )
#             loan.save()

#         return f"Loan data ingestion completed successfully!"

#     except Exception as e:
#         return f"Error: {str(e)}"
