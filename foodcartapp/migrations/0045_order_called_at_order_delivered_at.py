# Generated by Django 5.2.1 on 2025-06-23 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_alter_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called_at',
            field=models.DateField(blank=True, null=True, verbose_name='Дата звонка'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_at',
            field=models.DateField(blank=True, null=True, verbose_name='Дата доставка'),
        ),
    ]
