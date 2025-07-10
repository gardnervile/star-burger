from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from collections import defaultdict
from geolocation.models import Place
from django.utils.timezone import now
from datetime import timedelta
from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
import requests
from django.conf import settings
from requests.exceptions import RequestException
from geopy.distance import distance
from .geocoder import fetch_coordinates_from_yandex

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.exclude(status='Готов').prefetch_related('items__product')
    menu_items = RestaurantMenuItem.objects.select_related('restaurant', 'product').filter(availability=True)

    product_to_restaurants = defaultdict(set)
    for item in menu_items:
        product_to_restaurants[item.product_id].add(item.restaurant)
    restaurant_locations = {
        restaurant.id: fetch_coordinates(restaurant.address)
        for restaurant in Restaurant.objects.all()
    }
    orders_with_possible_restaurants = []
    for order in orders:
        restaurants_sets = [
            product_to_restaurants[item.product.id]
            for item in order.items.all()
            if item.product.id in product_to_restaurants
        ]

        if restaurants_sets:
            common_restaurants = set.intersection(*restaurants_sets)
        else:
            common_restaurants = set()

    orders_with_possible_restaurants = []

    for order in orders:
        restaurants_sets = [
            product_to_restaurants[item.product.id]
            for item in order.items.all()
            if item.product.id in product_to_restaurants
        ]

        if restaurants_sets:
            common_restaurants = set.intersection(*restaurants_sets)
        else:
            common_restaurants = set()

        order_location = fetch_coordinates(order.address)
        if not order_location:
            order.restaurants = []
            orders_with_possible_restaurants.append(order)
            continue

        distances = []
        for restaurant in common_restaurants:
            rest_coords = restaurant_locations.get(restaurant.id)
            if rest_coords:
                dist = get_distance_km(order_location, rest_coords)
                distances.append((restaurant, dist))

        distances.sort(key=lambda x: x[1])
        order.restaurants = [r for r, d in distances]
        order.distances = distances
        orders_with_possible_restaurants.append(order)

    orders_with_possible_restaurants.append(order)
    return render(request, template_name='order_items.html', context={
        'order_items': orders_with_possible_restaurants
    })


YA_GEOCODER_API_KEY = settings.YA_GEOCODER_API_KEY


def get_distance_km(point1, point2):
    return distance(point1, point2).km


def fetch_coordinates(address):
    try:
        place = Place.objects.get(address=address)

        if place.latitude and place.longitude and now() - place.updated_at < timedelta(days=30):
            return (place.latitude, place.longitude)

    except Place.DoesNotExist:
        place = Place.objects.create(address=address)

    coords = fetch_coordinates_from_yandex(address)

    if coords:
        latitude, longitude = coords
        place.latitude = latitude
        place.longitude = longitude

    place.updated_at = now()
    place.save()
    return coords
