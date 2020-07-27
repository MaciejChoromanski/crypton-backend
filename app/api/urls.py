from django.urls import path

from api import views


app_name = 'api'

urlpatterns = [
    path('user/create/', views.CreateUserView.as_view(), name='user_create'),
    path('user/me/', views.ManageUserView.as_view(), name='user_me'),
    path(
        'friend_request/create/',
        views.CreateFriendRequestView.as_view(),
        name='friend_request_create',
    ),
    path(
        'friend_request/list/',
        views.ListFriendRequestView.as_view(),
        name='friend_request_list',
    ),
    path(
        'friend_request/manage/<int:pk>/',
        views.ManageFriendRequestView.as_view(),
        name='friend_request_manage',
    ),
    path(
        'friend/create/',
        views.CreateFriendView.as_view(),
        name='friend_create',
    ),
]
