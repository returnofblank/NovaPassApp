from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='passapp-login'),
    path('dashboard/', views.dashboard, name='passapp-dashboard'),
    path('dashboard/pass/', views.pass_screen, name='passapp-pass'),
    path('api/end-pass/<int:pass_id>/', views.end_pass, name='passapp-endpass'),
    path('api/pass-status/<int:pass_id>/', views.pass_status, name='pass-status'),
    path('api/json-passes/', views.json_passes, name='passapp-pass-json'),
    path('download-passes/', views.download_passes, name='passapp-download'),
    path('logout/', views.user_logout, name='passapp-logout'),
]