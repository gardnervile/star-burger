# Generated by Django 5.2.1 on 2025-06-22 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_alter_order_status_alter_orderitem_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.CharField(default=0, verbose_name='Комментарий'),
            preserve_default=False,
        ),
    ]
