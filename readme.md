1.	创建"git文档"
2.	使用"github"下拉到本地
3.	打开."gitignore"文件任意位置添加".idea/"屏蔽上传
4.  导入前端文件"front_files"
5.  cd到"front_files"文件夹，打开命令行输入"  curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash"
6.  同级文件命令行输入"npm install -g live-server"；启动"live-server"
7.  经测试前端文件已启动进行后端文件配置
8.  进入"File | Settings | Project: djangoymx | Python Interpreter"添加虚拟环境
9.  进入"File | Settings | Project: djangoymx | Python Interpreter"添加Django，djangorestframework，pymysql，django_redis；如果安装异常使用命令行在虚拟环境下操作（pip install django==1.11.11  # 安装django；pip install djangorestframework  # 安装drf；pip install pymysql   #  安装pymsql；pip install django_redis  #安装redis数据库）
10. 打开Database添加Mysql数据库，输入账号密码，测试，根据测试结果进行调整，我遇到的问题是时区问题（改成UTC）
11. 根文档命令行输入"django-admin startproject mall"检测文档后发现成功获得mall文件夹
12. 进入到mall文件下，到达settings.py同级文件，新建测试文件settings | dev.py，然后将settings.py内容复制到dev.py中，随后删除settings.py
13. 进入manage.py中找到settings配置项修改成"os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings.dev')"(测试文件夹文件名均可改动只需要匹配即可)
14. 进入dev.py修改数据库配置项，（修改为
数据库配置项
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # 指定引擎
        'HOST': '127.0.0.1',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'root',  # 数据库用户名
        'PASSWORD': 'PTsrN4QXwzviL0D7',  # 数据库用户密码
        'NAME': 'mall'  # 数据库名字
    }
}
django-redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "redis_verifications": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/2",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

同时修改了Django的Session机制使用redis保存，且使用名为'session'的redis配置。

此处修改Django的Session机制存储主要是为了给Admin站点使用。

关于django-redis 的使用，说明文档可见http://django-redis-chs.readthedocs.io/zh_CN/latest/
http://doc.redisfans.com/
）
15. settings同级文件__init__.py添加"
from pymysql import install_as_MySQLdb
install_as_MySQLdb()
"
16. 以上数据库配置或出现错误，其一未找到相应名称的数据库，解决方法：在database中添加；其二redis数据库错误，找到最下方报错文件数据所指文件两行注销，问题解决
17. 修改设置项时区和区域本地化语言与时区
"
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
"
18. 添加日志功能
"LOGGING = {
    'version': 1,  # 保留子
    'disable_existing_loggers': False,  # 禁用在logger中的实例
    日志的格式
    'formatters': {
        # 详细一点的
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        # 简单一点的
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },

    那些日志可以从loggers传送到handlers
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    控制日志存放到哪里
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/mall_log.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    把日志传给handlers
    'loggers': {
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],
            'propagate': True,
        },
    }
}"
19. 在出现错误后发现是关于文件夹不存在的错误，在mall下新建logs文件夹，解除错误
20. 异常
修改Django REST framework的默认异常处理方法，补充处理数据库异常和Redis异常。

新建tools/exceptions.py

from rest_framework.views import exception_handler as drf_exception_handler
import logging
from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.response import Response
from rest_framework import status

获取在配置文件中定义的logger，用来记录日志
logger = logging.getLogger('django')

def exception_handler(exc, context):
    """
    自定义异常处理
    :param exc: 异常
    :param context: 抛出异常的上下文
    :return: Response响应对象
    """
    # 调用drf框架原生的异常处理方法
    response = drf_exception_handler(exc, context)

    if response is None:
        view = context['view']
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            # 数据库异常
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': '服务器内部错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response

配置文件中添加

异常
REST_FRAMEWORK = {
    # 异常处理
    'EXCEPTION_HANDLER': 'django_mall.tools.exceptions.exception_handler',
}
21. 注册drf到settings
"pip install djangorestframework

INSTALLED_APPS = [
    ...
    'rest_framework',   # drf注册
]"
22. settings同级新建apis文档，settings、dev添加
使用sys.path添加<BASE_DIR>/apis目录，
Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
添加导包路径
import sys
sys.path.insert(0, os.path.join(BASE_DIR, 'apis'))
23. \djangoymx\mall\mall\apis>python ../../manage.py startapp users 新建子应用，并添加到配置项
24. 添加模型类
"
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
"
配置项
自定义用户模型类
AUTH_USER_MODEL = 'users.User' # 子应用名.模型类名

'users.apps.UsersConfig'  # users 注册
25. python ../../manage.py makemigrations  # 创建迁移文件；python ../../manage.py migrate  # 执行迁移
26. 修改hosts文件"c:\windows\system32\drivers\etc"添加"127.0.0.1   www.mall.site;127.0.0.1   api.mall.site"
27. 跨域："pip install django-cors-headers"
28. 添加应用 INSTALLED_APPS = ('corsheaders',  # corsheaders注册)
29. MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware',  # 中间件 放到最上面]
30. 添加白名单CORS CORS_ORIGIN_WHITELIST = ('http://127.0.0.1:8080','http://localhost:8080','http://www.mall.site:8080','http://api.mall.site:8000')
31. CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie
32. 配合白名单域名 ALLOWED_HOSTS = ['127.0.0.1','localhost','www.mall.site','api.mall.site']
33. 新建子应用 mall/apis/verifications    "django-admin startapp verifications"
34. 添加 pip install Pillow 补齐文件包括，，，后续除具体问题外，不再书写，具体的放在xmind。

35. 出现cryptography is required for sha256_password or caching_sha2_password    安装 cryptography 
