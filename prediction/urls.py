from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('home/', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('predict/', views.predict_image, name='predict'),
    path('health/', views.health_check, name='health_check'),
    path('model-info/', views.model_info, name='model_info'),
    path('dataset/', views.dataset_view, name='dataset'),
    path('performance/', views.performance_view, name='performance'),
    path('report/', views.report_view, name='report'),
    path('parameters/', views.parameters_view, name='parameters'),
]
