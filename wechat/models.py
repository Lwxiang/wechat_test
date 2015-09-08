# coding=utf8

from django.db import models


class AccessToken(models.Model):
    token = models.CharField(u'access_token', max_length=1000)
    born_time = models.TimeField(auto_now_add=True)
    expires_in = models.IntegerField(u'有效时间')


class Restaurant(models.Model):
    name = models.CharField(u'店名', max_length=100, unique=True)
    address = models.CharField(u'地址', max_length=2000, blank=True, null=True)
    unique = models.CharField(u'特色', max_length=2000, blank=True, null=True)
    tel = models.CharField(u'电话', max_length=100, blank=True, null=True)