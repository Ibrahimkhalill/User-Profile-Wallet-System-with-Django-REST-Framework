from django.urls import path
from .views import register, user_profile, wallet_view
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('auth/register/', register, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', user_profile, name='profile'),
    path('wallet/', wallet_view, name='wallet'),
]
