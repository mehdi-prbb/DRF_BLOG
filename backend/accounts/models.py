from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin



class CustomUser(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(max_length=255, unique=True)
	phone_number = models.CharField(max_length=11, unique=True)
	full_name = models.CharField(max_length=255)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)


	USERNAME_FIELD = 'phone_number'
	REQUIRED_FIELDS = ['email', 'full_name']

	def __str__(self):
		return self.email

	@property
	def is_staff(self):
		return self.is_admin