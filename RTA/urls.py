from django.contrib import admin
from django.urls import path,include
from input.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
#    path('',include('input.urls')),
    path("",home,name="home"),
    path("user_signup", user_signup, name="user_signup"),
    path("user_login", user_login, name="user_login"),
    path("user_logout", user_logout, name="user_logout"),
    path("user_rp", user_rp, name="user_rp"),
    path("user_cp", user_cp, name="user_cp"),
    path('index',index, name="input"),
    path('index/input_form/count=<int:count>', input_form, name="input_form"),
    path('input_form/count=<int:count>', input_form, name="input_form"),
    path('index/input_form', error, name="input_from"),

]
