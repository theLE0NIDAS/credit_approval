from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string

class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        from background_task.models import Task
        from customers.tasks import ingest_customer_data
        from django.apps import apps 

        Customer = apps.get_model('customers', 'Customer')
        
        if not Task.objects.filter(task_name='customers.tasks.ingest_customer_data').exists():
            file_path = './excel_data/customer_data.xlsx'
            ingest_customer_task = import_string('customers.tasks.ingest_customer_data')
            ingest_customer_task(file_path)
