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
        'friend_request/<int:pk>/manage/',
        views.ManageFriendRequestView.as_view(),
        name='friend_request_manage',
    ),
    path(
        'friend/create/',
        views.CreateFriendView.as_view(),
        name='friend_create',
    ),
    path('friend/list/', views.ListFriendView.as_view(), name='friend_list'),
    path(
        'friend/<int:pk>/manage/',
        views.ManageFriendView.as_view(),
        name='friend_manage',
    ),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path(
        'message/create/',
        views.CreateMessageView.as_view(),
        name='message_create',
    ),
    path(
        'message/list/', views.ListMessageView.as_view(), name='message_list'
    ),
    path(
        'message/<int:pk>/manage',
        views.ManageMessageView.as_view(),
        name='message_manage',
    ),
]
