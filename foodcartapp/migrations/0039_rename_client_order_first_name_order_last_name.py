# Generated by Django 5.2.1 on 2025-05-14 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderitem'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='client',
            new_name='first_name',
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(default='Иванов', max_length=150, verbose_name='Фамилия'),
            preserve_default=False,
        ),
    ]
