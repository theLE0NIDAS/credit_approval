# Generated by Django 5.1.3 on 2024-11-14 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_alter_customer_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='current_debt',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
