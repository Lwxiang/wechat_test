# coding=utf8

from django.contrib import admin
from models import Restaurant


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'unique', 'tel')
    ordering = ('id',)


admin.site.register(Restaurant, RestaurantAdmin)
