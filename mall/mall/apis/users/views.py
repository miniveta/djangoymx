from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
# Create your views here.



class UserNameView(APIView):
    # 用户名数量
    def get(self, request, username):
        # 查询用户数量
        username_count = User.objects.filter(username = username).count()
        # 构造相应参数
        data = {
            "username": username,
            "count": username_count
        }
    return Response(data)


class MobileView(APIView):
    # 用户名mobile数量
    def get(self, request, mobile):
        # 查询用户mobile数量
        mobile_count = User.objects.filter(mobile = mobile).count()
        # 构造mobile相应参数
        data = {
            "username": mobile,
            "count": mobile_count
        }
    return Response(data)