from django.db import models

class Place(models.Model):
    address = models.CharField(max_length=255, unique=True, verbose_name='Адрес')
    latitude = models.FloatField(verbose_name='Широта', null=True, blank=True)
    longitude = models.FloatField(verbose_name='Долгота', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    def __str__(self):
        return self.address
