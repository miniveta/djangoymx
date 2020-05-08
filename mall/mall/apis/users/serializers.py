from django_redis import get_redis_connection
from rest_framework import serializers
import re

from .models import User

class UserSerializer(serializers.ModelSerializer):
    # 注册序列化器

    # 单独额外的校验校验　因为模型类没有　而且只做反序列化：write_only=True
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)

    class Meta:
        model = User
        # 'password2', 'sms_code', 'allow'  反序列化操作
        fields = ('id', 'username', 'password', 'mobile', 'password2', 'sms_code', 'allow')

        # 需要对原始模型类数据补存校验
        # 补存字段的校验
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

        # 单独校验
        # 校验用户的手机号码mobile必须和定义过的模型类的字段　或者单独额外的校验校验字段一致
        # data　初步校验过的数据　单一数据

    def validate_mobile(self, data):
        if not re.match(r'^1[3-9]\d{9}$', data):
            raise serializers.ValidationError("手机号码有误")
        return data

    def validate_allow(self, data):
        """用户协议"""
        if data != 'true':
            raise serializers.ValidationError("同意用户协议")
        return data

    # 联合校验 attrs多条数据
    def validate(self, attrs):
        """密码校验和短信验证码校验"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("密码不一致")

        redis_conn = get_redis_connection('redis_verifications')
        mobile = attrs['mobile']
        redis_sms_code = redis_conn.get("sms_%s" % mobile)
        if not redis_sms_code:
            raise serializers.ValidationError("无效的短信验证码")
        if redis_sms_code.decode() != attrs['sms_code']:
            raise serializers.ValidationError("短信验证码错误")

        return attrs

    def create(self, validated_data):
        """
        重写弗雷的create方法
        :param validated_data: 里面包含　password2　　sms_code　　allow
        :return:
        """
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 继承原来的crate方法　之前的不变
        user = super().create(validated_data)

        # 调用django的认证系统加密密码　password的字段以密文的形式展现
        user.set_password(validated_data['password'])

        # 调用save 将数据写入库
        user.save()

        # 响应
        return user
















