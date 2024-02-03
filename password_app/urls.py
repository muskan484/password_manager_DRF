from django.urls import path
from .views import (AddPassword,
                    ViewAllPassword,
                    UpdatePassword,
                    DeletePassword)

urlpatterns = [
    path('add',AddPassword.as_view()),
    path('all',ViewAllPassword.as_view()),
    path('update',UpdatePassword.as_view()),
    path('delete',DeletePassword.as_view())
]