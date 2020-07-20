from django.urls import path

from api import views


app_name = 'api'

urlpatterns = [
    path('user/create/', views.CreateUserView.as_view(), name='user_create'),
    path('user/me/', views.ManageUserView.as_view(), name='user_me'),
]
