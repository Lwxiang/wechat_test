# coding=utf8

import json
import hashlib

from django.http import HttpResponse

from wechat_test.settings import token


def checker(request):
    if request.method == "GET":
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        que = [token, timestamp, nonce]
        que.sort()
        sign = '%s%s%s' % tuple(que)
        sign = hashlib.sha1(sign).hexdigest()
        if signature == sign:
            return HttpResponse(echostr)
        else:
            return HttpResponse('INVALID')

