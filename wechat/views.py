# coding=utf8

import json
import hashlib

from django.http import HttpResponse
from wechat_sdk import WechatBasic

from wechat_test.settings import token
from models import Restaurant, User
from lib import RestaurantTemplate, get_access_token, check_user_enter
from lib import CHOOSE_FUNC_RESPONSE, ENTER_NAME_RESPONSE, ENTER_LCT_RESPONSE, ENTER_DISC_RESPONSE, \
    RES_LIST_RESPONSE, RES_NOT_FOUND_RESPONSE, LCT_NOT_FOUND_RESPONSE


def get(request):
    return HttpResponse(get_access_token())


def checker(request):
    if request.method == 'GET':

        # 公众号后台接入
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

        # 处理用户发送的信息
        body_text = request.body
        wechat = WechatBasic(token=token)
        wechat.parse_data(body_text)

        # 获取微信消息类WechatMessage
        message = wechat.get_message()

        # 获取用户openid
        openid = message.source
        try:
            user = User.objects.get(openid=openid)
        except User.DoesNotExist:
            user = User(openid=openid)
            user.save()

        response = None
        if message.type == 'text':

            if user.status == 'MASTER':
                if check_user_enter(message.content, 'NAME_INFO'):
                    user.status = 'NAME_INFO'
                    user.save()
                    response = wechat.response_text(ENTER_NAME_RESPONSE)
                elif check_user_enter(message.content, 'LCT_INFO'):
                    user.status = 'LCT_INFO'
                    user.save()
                    response = wechat.response_text(ENTER_LCT_RESPONSE)
                elif check_user_enter(message.content, 'DISC_INFO'):
                    user.status = 'DISC_INFO'
                    user.save()
                    response = wechat.response_text(ENTER_DISC_RESPONSE)
                else:
                    response = wechat.response_text(CHOOSE_FUNC_RESPONSE)

            elif user.status == 'NAME_INFO' or user.status == 'DISC_INFO':
                if message.content == u'退出':
                    user.status = 'MASTER'
                    user.save()
                    response = wechat.response_text(CHOOSE_FUNC_RESPONSE)
                else:
                    try:
                        restaurant = Restaurant.objects.get(name=message.content)
                        restaurant_template = RestaurantTemplate(restaurant=restaurant)
                        response = wechat.response_text(restaurant_template.response())
                    except Restaurant.DoesNotExist:
                        res_list = []
                        user.res_list = []
                        ful_name = message.content
                        if len(ful_name) in range(1, 7):
                            for i in range(len(ful_name), 0, -1):
                                for j in range(0, len(ful_name)-i+1):
                                    part_name = ful_name[j: i+j]
                                    try:
                                        restaurants = Restaurant.objects.filter(name__contains=part_name)
                                        for restaurant in restaurants:
                                            if not(restaurant.name in res_list):
                                                res_list.append(restaurant.name)
                                                user.res_list += ',' + restaurant.name
                                    except Restaurant.DoesNotExist:
                                        continue
                        user.save()
                        if res_list:
                            back_info = RES_LIST_RESPONSE
                            for k in range(0, len(res_list)):
                                back_info = "%s\n%d: %s" % (back_info, k, res_list[k])
                            response = wechat.response_text(back_info)
                        else:
                            response = wechat.response_text(RES_NOT_FOUND_RESPONSE)
            elif user.status == 'LCT_INFO':
                if message.content == u'退出':
                    user.status = 'MASTER'
                    user.save()
                    response = wechat.response_text(CHOOSE_FUNC_RESPONSE)
                else:
                    response = wechat.response_text(LCT_NOT_FOUND_RESPONSE)

        return HttpResponse(response)
