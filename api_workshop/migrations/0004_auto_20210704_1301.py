# Generated by Django 2.2.12 on 2021-07-04 06:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_workshop', '0003_auto_20210702_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice_item',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoide_details', to='api_workshop.invoice'),
        ),
    ]
