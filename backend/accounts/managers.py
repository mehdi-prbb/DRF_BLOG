from django.contrib.auth.models import BaseUserManager



class CustomUserManager(BaseUserManager):

	def create_user(self, phon_number, email, full_name, password):
		if not phon_number:
			raise ValueError('user must have phone number')

		if not email:
			raise ValueError('user must have email')

		if not full_name:
			raise ValueError('user must have full name')

		user = self.model(
			phon_number=phon_number,
			email=self.normalize_email(email),
			full_name=full_name
			)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, phon_number, email, full_name, password):
		
		 user = self.create_user(phon_number, email, full_name, password)
		 user.is_admin = True
		 user.is_superuser = True
		 user.save(using=self._db)