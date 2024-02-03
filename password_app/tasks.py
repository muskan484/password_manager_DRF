from celery import shared_task
from firebase_admin import storage
from password_manager import settings
from django.core.mail import send_mail
from password_manager.utility import weekly_report

@shared_task
def send_password_add_mail(target_mail, user, website_name):

    """
    This task sends an email notification to the user informing them that a new password
    has been successfully added to their account for a specific website.

    Parameters:
    - target_mail (str): The email address of the recipient.
    - user (str): The username of the user.
    - website_name (str): The name of the website for which the password was added.

    Returns: A message indicating that the email has been sent to the user.
    """
    
    mail_subject = "New Password Added Successfully!"
    message = f"Dear {user},\n\nWe are pleased to inform you that a new password for {website_name} has been added to your account successfully.\n\nThank you for entrusting us with your password management needs.\n\nBest regards,\nTeam Password Manager"
    send_mail(
        subject = mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[target_mail],
        fail_silently=False,
        )
    return f"Mail sent to {user} for adding new password"

@shared_task
def send_password_update_mail(target_mail, user, website_name):

    """
    This task sends an email notification to the user informing them that the password
    for a specific website in their account has been successfully updated.

    Parameters:
    - target_mail (str): The email address of the recipient.
    - user (str): The username of the user.
    - website_name (str): The name of the website for which the password was updated.

    Returns: A message indicating that the email has been sent to the user.
    """

    mail_subject = f"Password Updated for {website_name}"
    message = f"Dear {user},\n\nWe would like to inform you that the password for {website_name} has been successfully updated in your account.\n\nThank you for keeping your account secure and up-to-date.\n\nBest regards,\nTeam Password Manager"
    send_mail(
        subject = mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[target_mail],
        fail_silently=False,
        )
    return f"Mail sent to {user} for updating a password"

@shared_task
def upload_password_data_weekly_to_firebase():

    """
    This task uploads the weekly password data to Firebase Storage. It generates a JSON file
    containing the password data for the previous week and uploads it to the specified bucket
    in Firebase Storage.

    Returns: A message indicating the successful upload of the weekly data to Firebase Storage.
    """

    bucket = storage.bucket('password-manager-1307f.appspot.com')
    weekly_data,last_week,today = weekly_report()
    destination = f"weekly_data/password_data_{last_week.strftime("%Y-%m-%d")}_to_{today.strftime("%Y-%m-%d")}.json"
    blob = bucket.blob(destination)
    blob.upload_from_string(weekly_data, content_type='text/plain')
    return f"Weekly data uploaded to Firebase Storage: {destination}"