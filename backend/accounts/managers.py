from django.contrib.auth.models import BaseUserManager



class CustomUserManager(BaseUserManager):

	def create_user(self, phone_number, email, password):
		if not phone_number:
			raise ValueError('user must have phone number')

		if not email:
			raise ValueError('user must have email')

		user = self.model(
			phone_number=phone_number,
			email=self.normalize_email(email),
			)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, phone_number, email, password):
		
		user = self.create_user(phone_number, email, password)
		user.is_admin = True
		user.is_superuser = True
		user.save(using=self._db)