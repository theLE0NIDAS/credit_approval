from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string

class LoansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loans'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        from background_task.models import Task
        from loans.tasks import ingest_loan_data
        from django.apps import apps

        Loan = apps.get_model('loans', 'Loan')
        
        if not Task.objects.filter(task_name='loans.tasks.ingest_loan_data').exists():
            file_path = './excel_data/loan_data.xlsx'
            ingest_loan_task = import_string('loans.tasks.ingest_loan_data')
            ingest_loan_task(file_path)