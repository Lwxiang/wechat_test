# coding=utf8

import json
import hashlib

from django.http import HttpResponse
from wechat_sdk import WechatBasic

from wechat_test.settings import token
from models import Restaurant
from lib import RestaurantTemplate


def checker(request):
    if request.method == 'GET':
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')

        wechat = WechatBasic(token=token)
        if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponse(echostr)
        else:
            return HttpResponse('INVALID')

    else:
        body_text = request.body
        wechat = WechatBasic(token=token)
        wechat.parse_data(body_text)
        message = wechat.get_message()

        response = None
        if message.type == 'text':
            try:
                restaurant = Restaurant.objects.get(name=message.content)
                restmp = RestaurantTemplate(restaurant=restaurant)
                response = restmp.response()
            except:
                response = u'没有这家店'

        return HttpResponse(response)
