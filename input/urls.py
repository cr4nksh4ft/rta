from django.contrib import admin
from django.urls import path
from input import views

admin.site.site_header = "RTA Admin"
admin.site.site_title = "RTA Admin Portal"
admin.site.index_title = "Welcome to RTA Portal"

urlpatterns = [
    path('', views.index , name="input") ,
    path('input_form/count=<int:count>', views.input_form ,name="input_form"),
    path('input_form', views.error , name="input_from")
]
