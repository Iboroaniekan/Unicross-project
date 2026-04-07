from django.urls import path
from . import views

urlpatterns = [
    path('certificate/<str:cert_id>/', views.view_certificate, name='view_certificate'),
    # path('certificate/<str:cert_id>/download/', views.download_certificate, name='download_certificate'),
    path('verify-certificate/', views.verify_certificate, name='verify_certificate'),
    path('verify/<str:cert_id>/', views.verify_qr, name='verify_qr'),
]
