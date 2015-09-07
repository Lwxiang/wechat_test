# coding=utf8

import requests
import json

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
            s = s + u'地址: ' + self.unique + '\n'
        if self.tel:
            s = s + u'地址: ' + self.tel
        return s


def fresh_access_token():
    access_token = AccessToken.objects.get_or_create(id=1)
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=%s&appid=%s&secret=%s" \
          % (grant_type, appID, appSecret)
    r = requests.get(url)
    message = r.json()
    access_token.token = message['access_token']
    access_token.expires_in = message['expires_in']
    access_token.save()


def get_access_token():
    access_token = AccessToken.objects.get(id=1)
    return access_token.token




