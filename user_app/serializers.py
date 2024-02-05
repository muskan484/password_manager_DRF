from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style = {"input_style":"password"}, write_only = True)
    class Meta:
        model = User
        fields =["username", 'first_name', 'last_name', 'email', 'password' , 'confirm_password']
        extra_kwargs = {
            "password" : {"write_only":True}
        }

    def save(self):
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']
        if password != confirm_password:
            raise serializers.ValidationError({"Error":"Your password and confirmation password do not match."})
        
        if User.objects.filter(email = self.validated_data['email']).exists():
            raise serializers.ValidationError({"Error":"User already exists with this email id"})
        
        user_data = {
            'email':self.validated_data['email'],
            'username':self.validated_data['username'],
            'first_name':self.validated_data['first_name'],
            'last_name':self.validated_data['last_name']
        }
        account = User(**user_data)
        account.set_password(password)
        try:
            account.save() 
        except Exception as e:
            raise serializers.ValidationError({"Error": str(e)})
        return account
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", 'first_name', 'last_name', 'email', 'password','date_joined']
    
class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


