from rest_framework import serializers 
from .models import PasswordVault

class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordVault
        fields = "__all__"