from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from .views import Signup

urlpatterns = [
    path('', obtain_jwt_token, name='redirect_to_obtain_jwt_token'),
    path('login/', obtain_jwt_token, name='obtain_jwt_token'),
    path('api-token-refresh/', refresh_jwt_token, name='refresh_jwt_token'),
    path('signup/', Signup.as_view(), name='signup'),
]