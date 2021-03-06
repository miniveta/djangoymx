from django.conf.urls import url
from . import views
urlpatterns = [
    # ImageCodeView
    url('^image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
    # SMSCodeView
    url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
]