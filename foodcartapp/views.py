from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt

import json

from .models import Product, OrderItem, Order

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict


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

    if 'products' not in data:
        return Response({'products': 'Обязательное поле.'}, status=400)

    if data['products'] is None:
        return Response ({'products': 'Это поле не может быть пустым.'}, status=400)
    
    if not isinstance(data['products'], list):
        actual_type = type(data['products']).__name__
        return Response({'products': f'Ожидался list со значениями, но был получен "{actual_type}".'}, status=400)

    if not data['products']:
        return Response({'products': 'Этот список не может быть пустым.'}, status=400)
   

    order = Order.objects.create(
        client=data['firstname'],
        phonenumber=data['phonenumber'],
        address=data['address']
    )

    for item in data['products']:
        product = Product.objects.get(id=item['product'])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity']
        )

    return Response({'status': 'ok'}, status=status.HTTP_200_OK)

