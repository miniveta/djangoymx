from rest_framework import serializers
from django_redis import get_redis_connection
from redis import RedisError
import logging

loger = logging.getLogger('django')

class ImageSerializer(serializers.Serializer):   #图形验证码的序列化器

    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4, max_length=4)

    def validata(self, attrs):  # 校验图形验证码
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        redis_conn = get_redis_connection('redis_verifications')
        redis_text = redis_conn.get('img_%s' % image_code_id)

        if not redis_text:
            raise serializers.ValidationError('图形验证码不存在')

        # 删除图形验证码
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as r:
            loger.error(r)

        if redis_text.decode().lower() != text.lower():
            raise serializers.ValidationError('图形验证码错误')

        # 如果手机号存在不允许发送验证码
        mobile = self.context["view"].kwargs["mobile"]
        redis_flag_mobile = redis_conn.get("flag_%s" % mobile)
        if redis_flag_mobile:
            raise serializers.ValidationError("太频繁了")
        return attrs