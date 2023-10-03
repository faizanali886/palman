from django.urls import path, include
from .views import UserListCreateAPIView, UserDetailAPIView, CheckUserExistsAPIView, BotListCreateAPIView, BotDetailAPIView, AssignBotToUserAPIView,  AdminRegistrationAPIView, AdminLoginAPIView, AdminDetailAPIView

urlpatterns = [
    path('users/', UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('verify/<str:number>/', CheckUserExistsAPIView.as_view(), name='check-user-exists'),
    path('bots/', BotListCreateAPIView.as_view(), name='bot-list-create'),
    path('bots/<int:botid>/', BotDetailAPIView.as_view(), name='bot-detail'),
    
    path('users/<int:pk>/assign-bot/<int:bot_id>/', AssignBotToUserAPIView.as_view(), name='assign-bot-to-user'),
    path('admin/register/', AdminRegistrationAPIView.as_view(), name='admin-register'),
    path('admin/login/', AdminLoginAPIView.as_view(), name='admin-login'),
    path('admin/detail/', AdminDetailAPIView.as_view(), name='admin-detail'),
]