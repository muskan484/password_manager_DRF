from celery import shared_task
from password_manager import settings
from django.core.mail import send_mail

@shared_task
def send_welcome_mail(user, target_mail):
    """
    Task to send a welcome email to a new user.
    This task sends a welcome email to the specified user with a personalized message.
    It uses Django's send_mail function to send the email.

    Parameters:
    - user (str): Username of the new user.
    - target_mail (str): Email address of the new user.

    Returns: str: Confirmation message indicating that the welcome email has been sent.
    """
    mail_subject = "Welcome to Our Password Manager!"
    message = f"Dear {user},\n\nThank you for choosing our Password Manager!\n\nGet started by logging in to your account and securely store your passwords. You have full control to add, update, and delete passwords as needed. Rest assured, our system checks if your passwords have been compromised for added security.\n\nLogin now to experience hassle-free password management.\n\nBest regards,\nTeam Password Manager"
    send_mail(
        subject = mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[target_mail],
        fail_silently=False,
        )
    return f"Welcome mail sent to {user}"

