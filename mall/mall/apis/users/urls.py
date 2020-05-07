from django.conf.urls import url
from .import views

urlpatterns =[
    # UserNameView
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UserNameView.as_view()),

    # MobileView
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileView.as_view()),

    # UsersView
    url(r'^users/$', views.UsersView.as_view()),
]