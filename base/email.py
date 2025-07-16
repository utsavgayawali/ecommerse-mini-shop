from django.conf import settings
from django.core.mail import send_mail


def send_account_activateion_email(email, email_token):
 subject='Activate your accounts'
 email_form =settings.EMAIL_HOST_USER
 activation_link = f"http://127.0.0.1:8000/accounts/activate/{email_token}" 
 message=( 
        f"Hi there!\n\n"
        f"Thank you for registering.\n"
        f"Click the link below to activate your account:\n\n"
        f"{activation_link}\n\n"
        f"If you did not sign up, please ignore this email."
    )
    
 send_mail(subject, message, email_form,[email])