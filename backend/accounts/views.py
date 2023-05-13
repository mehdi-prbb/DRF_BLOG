import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserRegisterSerializer
from .models import OtpCode
from .custom_exceptions import DuplicatePhoneNumberException
from .utils import send_otp_code

class UserRegister(APIView):
    """
    Register new users using phone number and password.
    """
    serializer_class = UserRegisterSerializer

    def post(self, request):
        ser_data = UserRegisterSerializer(data=request.data)
        
        if ser_data.is_valid():
            random_code = random.randint(100000, 999999)

            try:
                OtpCode.objects.create(phone_number=ser_data.validated_data['phone_number'], code=random_code)
            except:
                raise DuplicatePhoneNumberException()
            

            send_otp_code(ser_data.data['phone_number'], random_code)

            email = ser_data.data.get('email')
            
            registration_info = {
                'phone_number': ser_data.validated_data['phone_number'],
                'password': ser_data.validated_data['password']
            }

            if email:
                registration_info['email'] = ser_data.validated_data['email']

            request.session['user_registration_info'] = registration_info

            # test it will be deleted
            print(request.session['user_registration_info'])
            
            return Response(ser_data.data, status=status.HTTP_308_PERMANENT_REDIRECT)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)
