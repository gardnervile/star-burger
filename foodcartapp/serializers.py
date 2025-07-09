from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from decimal import Decimal
from django.db import transaction

from .models import Order, OrderItem, Product


class OrderItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.Serializer):
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    phonenumber = PhoneNumberField()
    address = serializers.CharField()
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)
    items = OrderItemSerializer(source='item.all', many=True, read_only=True)
    
    def create(self, validated_data):
        products_data = validated_data.pop('products')
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for product_data in products_data:
                OrderItem.objects.create(
                    order=order,
                    product=product_data['product'],
                    quantity=product_data['quantity'],
                    price=Decimal(product_data['product'].price)
                )
        return order
    