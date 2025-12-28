from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pay/<int:project_id>/', views.pay, name='pay'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('download/<int:project_id>/', views.download, name='download'),
    path('create-superuser/', views.create_superuser),
    path('run-migrations/', views.migrate_site),
]
