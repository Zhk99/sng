import pyotp
from decouple import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework import status
from .models import User
from twilio.rest import Client as TwilioClient


def send_user_activation_email(user, email):
    mail_subject = 'Activate your account'
    message = render_to_string('activation_email.html', {
        'user': user,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    email = EmailMessage(mail_subject, message, to=[email])
    email.send()


def activation_user(uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        customer = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError):
        customer = None
    if customer is not None and default_token_generator.check_token(customer, token):
        customer.is_active = True
        customer.save()
        msg = {'message': 'Thank you for your email confirmation. Now you can login your account.'}
        return Response(msg, status=status.HTTP_200_OK)
    else:
        msg = {'message': 'Activation link is invalid!'}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)


def encode_uid(pk):
    return force_text(urlsafe_base64_encode(force_bytes(pk)))


def decode_uid(pk):
    return force_text(urlsafe_base64_decode(pk))


account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config("TWILIO_AUTH_TOKEN")
twilio_phone = config("TWILIO_PHONE")
client = TwilioClient(account_sid, auth_token)


def send_sms_code(request, format=None):
    # Time based otp
    time_otp = pyotp.TOTP(request.user.key, interval=300)
    time_otp = time_otp.now()
    user_phone_number = request.user.phonenumber.number  # Must start with a plus '+'
    client.messages.create(
        body="Your verification code is " + time_otp,
        from_=twilio_phone,
        to=user_phone_number
    )
