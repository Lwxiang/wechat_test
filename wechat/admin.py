# coding=utf8

from django.contrib import admin
from models import Restaurant, AccessToken, User


class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'born_time', 'expires_in')


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'unique', 'tel')
    ordering = ('id',)


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'openid', 'remark', 'status')


admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(User, UserAdmin)
