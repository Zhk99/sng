import pyotp
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .manager import UserManager


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """Base user model"""
    email = models.EmailField(max_length=255, unique=True, db_index=True, verbose_name='Email')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated = models.DateTimeField(auto_now=True, verbose_name='Updated')
    key = models.CharField(max_length=100, unique=True, blank=True)
    phone_number = models.CharField(max_length=200, blank=True, null=True, verbose_name='Phone number')
    is_staff = models.BooleanField(default=False, verbose_name='Is staff')
    is_active = models.BooleanField(default=True, verbose_name='Is active')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def authenticate(self, otp):
        """ This method authenticates the given otp"""
        provided_otp = 0
        try:
            provided_otp = int(otp)
        except:
            return False
        t = pyotp.TOTP(self.key, interval=300)
        return t.verify(provided_otp)

    class Meta:
        ordering = ['-created']
        verbose_name = 'User'
        verbose_name_plural = 'Users'


@receiver(post_save)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if issubclass(sender, User) and created:
        Token.objects.create(user=instance)