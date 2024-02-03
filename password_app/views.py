from rest_framework import views
from rest_framework import status
from .models import PasswordVault
from django.contrib.auth.models import User
from .serializers import PasswordSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from password_app.tasks import send_password_add_mail, send_password_update_mail
from password_manager.utility import (check_password_strength,
                                      generate_password,
                                      decrypt_password,
                                      encrypt_password)

class AddPassword(views.APIView):

    """
    This view handles POST requests to add a new password entry. The request
    must include data containing details about the password entry, such as the
    website name and optionally the password. If the 'autogenerate' query parameter
    is provided and set to true, the view automatically generates a secure password.

    Parameters:
    - request (Request): HTTP request object containing password entry data.
    - autogenerate (str): Optional query parameter indicating whether to autogenerate a password.
    Return: Response: JSON response indicating the success or failure of the password addition.
    """

    def post(self, request, *args, **kwargs):
        autogenerate = request.GET.get('autogenerate')
        data = request.data
        current_user = request.user.username
        data['user'] = current_user
        data['website_name'] = data['website_name'].lower()
        email = User.objects.get(username = current_user).email
        if PasswordVault.objects.filter(user=current_user, website_name=(data['website_name']).lower()).exists():
            raise ValidationError({"Error": f"Passwords for '{data['website_name']}' already exist. Consider updating the existing password for enhanced security."})

        if autogenerate:
            data['password'] = generate_password()

        serializer = PasswordSerializer(data=data)
        
        if serializer.is_valid():
            raw_data = serializer.validated_data
            resultant_data = check_password_strength(raw_data)
            if isinstance(resultant_data, Response):
                return resultant_data
            else:
                serializer.validated_data['password'] = resultant_data['password']
                serializer.save()
                send_password_add_mail.delay(email, current_user, resultant_data['website_name'])
                return Response({"Message": f"Password for {serializer.validated_data['website_name']} has been added successfully"}, status=status.HTTP_201_CREATED)
        raise ValidationError(serializer.errors)
    
class ViewAllPassword(views.APIView):
    """
    View to retrieve all password entries for the authenticated user.
    This view handles GET requests to retrieve all password entries associated
    with the authenticated user. It returns a JSON response containing details of
    all the password entries.

    Parameters:
    - request (Request): HTTP GET request object.
    - current_user (str): Username of the authenticated user.

    Return: Response: JSON response containing details of all the password entries associated with the authenticated user.
    """
    def get(self, request, *args, **kwargs):
        current_user = request.user.username
        all_entries = PasswordVault.objects.filter(user=current_user).values()
        for data in all_entries:
            data['password'] = decrypt_password(data['password'])
        return Response(all_entries)

class UpdatePassword(views.APIView):

    """
    View to update a password entry.
    This view handles POST requests to update a password entry for the authenticated user.
    It expects 'old_password', 'new_password', 'website_name', and 'website_url' keys in the request data.

    Parameters:
    - request (Request): HTTP POST request object.
    - current_user (str): Username of the authenticated user.
    - email (str): Email associated with the authenticated user.
    - data (dict): Dictionary containing request data.

    Returns: Response: JSON response indicating the status of the password update request.
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        current_user = request.user.username
        email = User.objects.get(username = current_user).email
        if 'old_password' not in data.keys() or 'new_password' not in data.keys():
            return Response({"Error":"old_password/new_password key is required"}, status=status.HTTP_400_BAD_REQUEST)
        encrypted_old_password = encrypt_password(data['old_password'])
        try:
            user_info = PasswordVault.objects.get(user = current_user, website_name = data['website_name'], website_url = data['website_url'])
            if user_info.password != encrypted_old_password:
                return Response({"Error": "Old password does not match."}, status=status.HTTP_400_BAD_REQUEST)
            
            encrypted_new_password = encrypt_password(data['new_password'])
            user_info.password = encrypted_new_password
            user_info.save(update_fields=['password'])

            send_password_update_mail.delay(email,current_user,user_info.website_name)
            return Response({"Message":f"Password for {data['website_name']} updated successfully."},status=status.HTTP_200_OK) 
        except PasswordVault.DoesNotExist:
            return Response({"Error": "Invalid data provided. Please ensure that the input is accurate and complete."}, status=status.HTTP_404_NOT_FOUND)

class DeletePassword(views.APIView):

    """
    View to delete a password entry.
    This view handles GET requests to delete a password entry for the authenticated user.
    It expects 'website_name' key in the request query parameters.

    Parameters:
    - request (Request): HTTP GET request object.
    - current_user (str): Username of the authenticated user.
    - website_name (str): Name of the website for which the password entry needs to be deleted.

    Returns: JSON response indicating the status of the password deletion request.
    """
        
    def get(self,request,*args,**kwargs):
        website_name = request.GET.get('website_name')
        current_user = request.user.username
        if not website_name:
            return Response({"Error": "Website_name required"}, status=status.HTTP_404_NOT_FOUND)
        try:
            password_info = PasswordVault.objects.get(user = current_user, website_name = website_name)
            password_info.delete()
            return Response({"Message":f"Password for {website_name} deleted successfully"},status=status.HTTP_200_OK)
        except:
            return Response({"Error":f"No password found for {website_name}"},status=status.HTTP_404_NOT_FOUND)

