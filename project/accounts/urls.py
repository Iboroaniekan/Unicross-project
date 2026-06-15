from django.urls import path
from .views import admin_login
from django.contrib.auth import views as auth_views



app_name = "accounts"

urlpatterns = [
    path("login/", admin_login, name="admin_login"),

]
