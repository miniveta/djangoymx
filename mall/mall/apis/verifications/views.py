from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView,CreateAPIView

import logging
import random

# 第三方插件
from mall.third_partys.captcha.captcha import captcha
from mall.third_partys.sms_code.sms import SendSMS
from .serializers import ImageSerializer

loger = logging.getLogger('django')

class ImageCodeView(APIView):   # 图形验证码
    def get(self, request, image_code_id):  # 发送图形验证码
        # 1 生成图形验证码
        text, image = captcha.generate_captcha()
        loger.info(text)
        # 2 接收用户uuid
        redis_conn = get_redis_connection('redis_verifications')

        # 3 绑定uuid和验证码
        redis_conn.setex("img_%s"% image_code_id, 300, text)

        # 4 响应生成
        return HttpResponse(image, content_type="img/jpg")

class SMSCodeView(GenericAPIView):  #短信验证码
    serializer_class = ImageSerializer

    def get(self, request, mobile): # 发送短信验证码
        # 数据校验
        data = request.query_params
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception= True)

        # 生成短信验证码 不足6位用0补
        sms_code = '%06d' % random.randint(0, 999999)
        loger.info(sms_code)

        # 保存短信验证码
        redis_conn = get_redis_connection('redis_verifications')
        redis_conn.setex("sms_%s" % mobile, 300, sms_code)

        # 保存手机号码　后面的验证码60秒只能发送一次使用
        redis_conn.setex("flag_%s" % mobile, 60, mobile)

        # 发送短信验证码
        # mobile:手机号　, [sms_code：短信验证码的内容, 5：过期时间], 1：模板一免费的必须用它
        SendSMS().send_template_sms(mobile, [sms_code, 5], 1)

        # 响应
        return Response({"message": "ok"})