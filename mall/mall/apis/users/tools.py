import re
from django.contrib.auth.backends import ModelBackend

from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    由于我们的jwt　响应的数据只有token　
    当时我们需要用户名和id所以我们需要让django框架取认识我们自定义的响应
    自定义状态保持的响应内容
    :param token: token
    :param user: 用户名
    :param request: 请求对象
    :return: token,username,id
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_username_mobile_account(account):
    """
    跟据帐号获取user对象
    :param caaount: 用户名或者手机号
    :return: user对象或者None
    """
    try:
        if re.match(r"1[3-9]\d{9}", account):
            user = User.objects.get(mobile=account)

        else:
            user = User.objects.get(username=account)

    except User.DoesNotExist:
        return None

    return user


class UsernameMobileLogin(ModelBackend):
    """
    由于我们需要多张好登录
    所以需要重写ＪＷＴ的认证　　ModelBackend的方法authenticate
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """重写父类的认证"""

        user = get_username_mobile_account(username)
        if user is not None and user.check_password(password):
            return user