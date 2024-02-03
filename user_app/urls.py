from django.urls import path
from .views import RegisterUser, LoginUser

urlpatterns = [
    path('register',RegisterUser.as_view()),
    path('login',LoginUser.as_view()),
]