from rest_framework import serializers
from foodcartapp.models import Order, OrderItem, Product
from phonenumber_field.serializerfields import PhoneNumberField
from decimal import Decimal
from django.db import transaction


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    phonenumber = PhoneNumberField()
    products = OrderItemSerializer(many=True, write_only=True)
    items = OrderItemSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products', 'items']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            items = [
                OrderItem(
                order=order,
                product=product_data['product'],
                quantity=product_data['quantity'],
                price=Decimal(product_data['product'].price)
            )
            for product_data in products_data
        ]
            OrderItem.objects.bulk_create(items)
        
        return order
