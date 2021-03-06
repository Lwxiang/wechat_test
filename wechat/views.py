# coding=utf8

import json
import hashlib

from django.http import HttpResponse
from wechat_sdk import WechatBasic

from wechat_test.settings import token
from models import Restaurant, User
from lib import RestaurantTemplate, get_access_token, check_user_enter, name_searcher, location_searcher, \
    location_recommend, distance_recommend
from lib import CHOOSE_FUNC_RESPONSE, ENTER_NAME_RESPONSE, ENTER_LCT_RESPONSE, ENTER_DISC_RESPONSE, \
    RES_LIST_RESPONSE, RES_NOT_FOUND_RESPONSE, LCT_NOT_FOUND_RESPONSE, NAME_CHOOSE_ERROR_RESPONSE, \
    ENTER_NUM_RESPONSE, ENTER_ROLL_RESPONSE


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
                        res_list, user.res_list = name_searcher(message.content)
                        user.save()

                        if res_list:
                            if user.status == 'NAME_INFO':
                                user.status = 'NAME_CHOOSE'
                                user.save()

                            else:
                                user.status == 'DISC_CHOOSE'
                                user.save()

                            back_info = RES_LIST_RESPONSE
                            for k in range(0, len(res_list)):
                                back_info = "%s\n%d: %s" % (back_info, k+1, res_list[k])
                            back_info += ENTER_NUM_RESPONSE
                            response = wechat.response_text(back_info)

                        else:
                            response = wechat.response_text(RES_NOT_FOUND_RESPONSE)

            elif user.status == 'LCT_INFO':
                if message.content == u'退出':
                    user.status = 'MASTER'
                    user.save()
                    response = wechat.response_text(CHOOSE_FUNC_RESPONSE)

                else:
                    if user.lct and message.content == '0':
                        restaurant = location_recommend(user, 0.7)
                        restaurant_template = RestaurantTemplate(restaurant=restaurant)
                        response = wechat.response_text(restaurant_template.response() + ENTER_ROLL_RESPONSE)

                    else:
                        lct_list, user.lct_list = location_searcher(message.content)
                        user.save()
                        if lct_list:
                            user.lct = message.content
                            user.save()
                            restaurant = location_recommend(user, 0.7)
                            restaurant_template = RestaurantTemplate(restaurant=restaurant)
                            response = wechat.response_text(restaurant_template.response() + ENTER_ROLL_RESPONSE)

                        else:
                            user.lct = ''
                            user.save()
                            response = wechat.response_text(LCT_NOT_FOUND_RESPONSE)

            elif user.status == 'NAME_CHOOSE':
                if message.content == u'退出':
                    user.status = 'NAME_INFO'
                    user.save()
                    response = wechat.response_text(ENTER_NAME_RESPONSE)

                else:
                    res_list = user.res_list.split(',')
                    try:
                        index = int(message.content)
                        if not (index in range(1, len(res_list))):
                            raise ValueError

                        restaurant = Restaurant.objects.get(id=int(res_list[index]))
                        restaurant_template = RestaurantTemplate(restaurant=restaurant)
                        response = wechat.response_text(restaurant_template.response())

                    except ValueError:
                        response = wechat.response_text(NAME_CHOOSE_ERROR_RESPONSE)

        elif message.type == 'location' and user.status == 'LCT_INFO':
            latitude = float(message.location[0])
            longitude = float(message.location[1])
            user.lct_list = distance_recommend(latitude, longitude)
            user.save()
            if user.lct_list:
                user.lct = message.label
                user.save()
                restaurant = location_recommend(user, 0.7)
                restaurant_template = RestaurantTemplate(restaurant=restaurant)
                response = wechat.response_text(restaurant_template.response() + ENTER_ROLL_RESPONSE)

            else:
                user.lct = ''
                user.save()
                response = wechat.response_text(LCT_NOT_FOUND_RESPONSE)

        else:
            response = wechat.response_text(ENTER_NAME_RESPONSE)

        return HttpResponse(response)
