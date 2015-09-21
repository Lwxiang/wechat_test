# coding=utf8

from django.db import models


SEX_CHOICE = (
    (u'位置', 0),
    (u'男性', 1),
    (u'女性', 2)
)


class AccessToken(models.Model):
    token = models.CharField(u'access_token', max_length=1000)
    born_time = models.DateTimeField(auto_now_add=True)
    expires_in = models.IntegerField(u'有效时间')

    def __unicode__(self):
        return self.token


class Restaurant(models.Model):
    name = models.CharField(u'店名', max_length=100, unique=True)
    address = models.CharField(u'地址', max_length=2000, blank=True, null=True)
    unique = models.CharField(u'特色', max_length=2000, blank=True, null=True)
    tel = models.CharField(u'电话', max_length=100, blank=True, null=True)
    longitude = models.FloatField(u'经度', max_length=100)
    latitude = models.FloatField(u'纬度', max_length=100)
    recommend = models.BooleanField(u'是否推荐', default=False)

    def __unicode__(self):
        return self.name


class User(models.Model):
    openid = models.CharField(u'用户ID', max_length=100, unique=True)
    # nickname = models.CharField(u'用户昵称', max_length=100)
    # sex = models.CharField(u'性别', choices=SEX_CHOICE)
    # city = models.CharField(u'所在城市', max_length=100, blank=True, null=True)
    remark = models.CharField(u'备注', max_length=1000, blank=True, null=True)
    status = models.CharField(u'消息状态', max_length=100, default='MASTER')
    res_list = models.CharField(u'名字备选餐厅列表', max_length=1000, blank=True, null=True)
    lct_list = models.CharField(u'地点备选餐厅列表', max_length=1000, blank=True, null=True)
    lct = models.CharField(u'搜索地点', max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.openid


