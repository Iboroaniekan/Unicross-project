from django.urls import path
from .views import admin_login,signup



app_name = "accounts"

urlpatterns = [
    path("login/", admin_login, name="admin_login"),
    path('signup/', signup, name='signup'),
    
]