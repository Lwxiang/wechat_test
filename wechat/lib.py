# coding=utf8

import datetime

import requests

from wechat_test.settings import grant_type, appID, appSecret
from models import AccessToken


class RestaurantTemplate:
    def __init__(self, restaurant):
        self.name = restaurant.name
        self.address = restaurant.address
        self.unique = restaurant.unique
        self.tel = restaurant.tel

    def response(self):
        s = ''
        s = s + u'店名: ' + self.name + '\n'
        if self.address:
            s = s + u'地址: ' + self.address + '\n'
        if self.unique:
            s = s + u'特色: ' + self.unique + '\n'
        if self.tel:
            s = s + u'电话: ' + self.tel
        return s


def fresh_access_token():
    try:
        access_token = AccessToken.objects.get(id=1)
    except AccessToken.DoesNotExist:
        access_token = AccessToken()
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=%s&appid=%s&secret=%s" \
          % (grant_type, appID, appSecret)
    r = requests.get(url)
    message = r.json()
    access_token.token = message['access_token']
    access_token.expires_in = int(message['expires_in'])
    access_token.save()


def get_access_token():
    try:
        access_token = AccessToken.objects.get(id=1)
        if (datetime.datetime.now() - access_token.born_time.replace(tzinfo=None)).seconds >= access_token.expires_in:
            fresh_access_token()
            access_token = AccessToken.objects.get(id=1)
    except AccessToken.DoesNotExist:
        fresh_access_token()
        return get_access_token()
    return access_token.token




