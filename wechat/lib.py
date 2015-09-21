# coding=utf8

import datetime
from random import choice, randint

import requests

from wechat_test.settings import grant_type, appID, appSecret
from models import AccessToken, Restaurant


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


def check_user_enter(content, string):
    if string == 'NAME_INFO':
        if content == '1' or content == u'吃':
            return True
        else:
            return False
    if string == 'LCT_INFO':
        if content == '2' or content == u'哪':
            return True
        else:
            return False
    if string == 'DISC_INFO':
        if content == '3' or content == u'省':
            return True
        else:
            return False


def name_searcher(ful_name):
    res_list = []
    user_res_list = ''
    if len(ful_name) in range(1, 7):
        for i in range(len(ful_name), 0, -1):
            for j in range(0, len(ful_name)-i+1):
                part_name = ful_name[j: i+j]
                try:
                    restaurants = Restaurant.objects.filter(name__contains=part_name)
                    for restaurant in restaurants:
                        if not(restaurant.name in res_list):
                            res_list.append(restaurant.name)
                            user_res_list += ',' + str(restaurant.id)
                except Restaurant.DoesNotExist:
                    continue
    return res_list, user_res_list


def location_searcher(ful_lct):
    lct_list = []
    user_lct_list = ''
    if len(ful_lct) in range(1, 7):
        for i in range(len(ful_lct), 0, -1):
            for j in range(0, len(ful_lct)-i+1):
                part_lct = ful_lct[j: i+j]
                try:
                    restaurants = Restaurant.objects.filter(address__contains=part_lct)
                    for restaurant in restaurants:
                        if not(restaurant.id in lct_list):
                            lct_list.append(restaurant.id)
                            user_lct_list += ',' + str(restaurant.id)
                except Restaurant.DoesNotExist:
                    continue
    return lct_list, user_lct_list


def location_recommend(user, rate):
    que = user.lct_list
    while True:
        rid = choice(que)
        restaurant = Restaurant.objects.get(id=rid)
        rand_rate = randint(0, 1)
        if restaurant.recommend and rand_rate < rate:
            return restaurant
        if not restaurant.recomend and rand_rate > rate:
            return restaurant


CHOOSE_FUNC_RESPONSE = u'嗨～欢迎使用吃乎～菌菌提醒你——\n' +\
                       u'回复"1"或"吃"，查找店名～\n' +\
                       u'回复"2"或"哪"，查找地点～\n' +\
                       u'回复"3"或"省"，查找代金券~'

ENTER_NAME_RESPONSE = u'回复店名（如“汉堡王”）就能获取店铺信息以及小编们非常（bu）靠谱的特色菜推荐~'

ENTER_LCT_RESPONSE = u'回复你将用餐的地点（如“珞狮路”、“群光”、“群光7楼”），或是直接发送定位给菌菌，菌菌会帮你随机推荐一家店铺哦o((*^▽^*))o'

ENTER_DISC_RESPONSE = u'回复店名（如“汉堡王”）就能获取店铺代金券以及更多优惠信息~\(≧▽≦)/~'

RES_LIST_RESPONSE = u'没有找到完全符合的店名（＞д＜）亲爱的你要找的是不是这些店铺'

RES_NOT_FOUND_RESPONSE = u'没有这家店'

LCT_NOT_FOUND_RESPONSE = u'菌菌也找不到这附近的店铺啦o(╥﹏╥)o 要不要试试其他地点呢'

NAME_CHOOSE_ERROR_RESPONSE = u'菌菌还在等你选择上述的店铺哟，回复“退出”回到查找店名～'