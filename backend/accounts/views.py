import pytz
import random
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from .serializers import UserRegisterSerializer, OtpVerifySerializer
from .models import OtpCode, CustomUser
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
            
            return Response(ser_data.data, status=status.HTTP_308_PERMANENT_REDIRECT)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpVerify(APIView):
    """
    get otp code from user to verify it.
    """

    def post(self, request):
        user_session = request.session['user_registration_info']

        check_expiration = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)

        ser_code = OtpVerifySerializer(data=request.data)

        if ser_code.is_valid():

            try:
                code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
            except ObjectDoesNotExist:
                return Response({'message':'ObjectDoesNotExist'}, status=status.HTTP_400_BAD_REQUEST)
            
            if code_instance.created < check_expiration:
                code_instance.delete()
                return Response({'message':'code expired'}, status=status.HTTP_408_REQUEST_TIMEOUT)
            
            elif ser_code.data['code'] == code_instance.code:
                CustomUser.objects.create_user(**user_session)
                code_instance.delete()
                del user_session
                return Response({'message':'new account created'}, status=status.HTTP_201_CREATED)
        
        return Response({'message':'invalid input'}, status=status.HTTP_400_BAD_REQUEST)
    
