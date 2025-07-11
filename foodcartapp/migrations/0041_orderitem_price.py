# Generated by Django 5.2.1 on 2025-06-15 14:31

import django.core.validators
from django.db import migrations, models


def set_prices_for_old_items(apps, schema_editor):
    OrderItem = apps.get_model('foodcartapp', 'OrderItem')
    Product = apps.get_model('foodcartapp', 'Product')

    for item in OrderItem.objects.filter(price__isnull=True):
        item.price = item.product.price
        item.save()

        
class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_rename_first_name_order_firstname_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=8, validators=[django.core.validators.MinValueValidator('0.00')], verbose_name='Цена'),
            preserve_default=False,
        ),
    ]
