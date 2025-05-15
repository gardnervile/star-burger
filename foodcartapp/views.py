from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt

import json

from .models import Product, OrderItem, Order

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict

import phonenumbers


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    data = request.data
    errors = {}

    # === Проверка полей заказа ===
    for field in ['firstname', 'lastname', 'phonenumber', 'address']:
        if field not in data:
            errors[field] = 'Обязательное поле.'
        elif data[field] is None or data[field] == '':
            errors[field] = 'Это поле не может быть пустым.'
        elif not isinstance(data[field], str):
            errors[field] = 'Недопустимый тип. Ожидалась строка.'

    # === Проверка поля products ===
    if 'products' not in data:
        errors['products'] = 'Обязательное поле.'
    elif data['products'] is None:
        errors['products'] = 'Это поле не может быть пустым.'
    elif not isinstance(data['products'], list):
        actual_type = type(data['products']).__name__
        errors['products'] = f'Ожидался list со значениями, но был получен "{actual_type}".'
    elif not data['products']:
        errors['products'] = 'Этот список не может быть пустым.'

    # === Остановиться, если уже есть ошибки ===
    if errors:
        return Response(errors, status=400)

    # === Проверка каждого элемента products ===
    order_items = []
    for index, item in enumerate(data['products']):
        if not isinstance(item, dict):
            return Response({'products': f'Элемент №{index + 1} должен быть словарём.'}, status=400)

        if 'product' not in item:
            return Response({'products': f'В элементе №{index + 1} отсутствует ключ "product".'}, status=400)

        if 'quantity' not in item:
            return Response({'products': f'В элементе №{index + 1} отсутствует ключ "quantity".'}, status=400)

        # Проверка quantity
        quantity = item['quantity']
        if not isinstance(quantity, int) or quantity <= 0:
            return Response({'products': f'quantity должен быть положительным числом в элементе №{index + 1}.'}, status=400)

        # Проверка, существует ли продукт
        try:
            product = Product.objects.get(id=item['product'])
        except Product.DoesNotExist:
            return Response({'products': f'Недопустимый первичный ключ "{item["product"]}"'}, status=400)

        order_items.append({'product': product, 'quantity': quantity})

        try:
            phone_obj = phonenumbers.parse(data['phonenumber'], None)
            if not phonenumbers.is_valid_number(phone_obj):
                return Response({'phonenumber': 'Введен некорректный номер телефона.'}, status=400)
        except phonenumbers.NumberParseException:
            return Response({'phonenumber': 'Введен некорректный номер телефона.'}, status=400)

    # === Всё ок — создаём заказ и позиции ===
    order = Order.objects.create(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=data['phonenumber'],
        address=data['address']
    )

    for item in order_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity']
        )

    return Response({'status': 'ok'}, status=200)
