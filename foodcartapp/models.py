from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from decimal import Decimal

class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    firstname = models.CharField(max_length=150, verbose_name='Имя')
    lastname = models.CharField(max_length=150, verbose_name='Фамилия')
    phonenumber = PhoneNumberField(verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    called_at = models.DateTimeField(auto_now_add=False, verbose_name='Дата звонка', null=True, blank=True)
    delivered_at = models.DateTimeField(auto_now_add=False, verbose_name='Дата доставка', null=True, blank=True)
    comment = models.CharField(verbose_name='Комментарий', blank=True)
    payment_method = models.CharField(
        max_length=15,
        choices=[
            ('Наличные', 'Наличные'),
            ('Электронно', 'Электронно')
        ],
        default='Наличные',
        verbose_name='Способ оплаты',
        )
    STATUS_CHOISES = [
        ('Новый', 'Новый'),
        ('В сборке', 'В сборке'),
        ('Готовится', 'Готовится'),
        ('Доставляется', 'Доставляется'),
        ('Готов', 'Готов'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOISES,
        default='Новый',
        verbose_name='Статус'
    )
    restaurant = models.ForeignKey(
        'Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Ресторан, готовящий заказ'
    )

    def __str__(self):
        return f'Заказ #{self.id} — {self.firstname} {self.lastname}'

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['-created_at']


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name='Заказ'
    )
    price = models.DecimalField(
        validators=[MinValueValidator(Decimal('0.00'))],
        null=False,
        blank=False,
        verbose_name='Цена',
        max_digits=8,
        decimal_places=2
    )
    def __str__(self):
        return f'{self.product.name} × {self.quantity} (заказ #{self.order.id})'

    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'позиции заказа'