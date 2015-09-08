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
                restaurant_template = RestaurantTemplate(restaurant=restaurant)
                response = wechat.response_text(restaurant_template.response())
            except Restaurant.DoesNotExist:
                res_list = []
                ful_name = message.content
                if len(ful_name) in range(2, 7):
                    for i in range(len(ful_name)-1, 1, -1):
                        for j in range(0, len(ful_name)-i+1):
                            part_name = ful_name[j: i+j]
                            try:
                                restaurants = Restaurant.objects.filter(name__contains=part_name)
                                for restaurant in restaurants:
                                    if not(restaurant.name in res_list):
                                        restaurant.append(restaurant.name)
                            except Restaurant.DoesNotExist:
                                continue
                if res_list:
                    back_info = u'没有找到完全符合的店名哦～亲爱的你要找的是不是这些店铺'
                    for k in range(0, len(res_list)):
                        back_info = "%s\n%d: %s" % (back_info, k, res_list[k])
                    response = wechat.response_text(back_info)
                else:
                    response = wechat.response_text(u'没有这家店')

        return HttpResponse(response)
