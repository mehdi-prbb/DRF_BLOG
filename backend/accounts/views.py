import pytz
import random
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


from .models import OtpCode, CustomUser
from .custom_exceptions import DuplicatePhoneNumberException
from .utils import send_otp_code
from .serializers import (UserRegisterSerializer,
                          OtpVerifySerializer,
                          LoginSerializer,
                          LogoutSerializer,
                          changePasswordSerializer,)

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

    serializer_class = OtpVerifySerializer

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
    

class LoginView(APIView):

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.data['email_or_phone']
            password = serializer.data['password']

            user = authenticate(request, username=email_or_phone, password=password)

            if user is not None:
                login(request, user)

                refresh = RefreshToken.for_user(user)
        
                return Response({
                                'refresh_token': str(refresh),
                                'access_token': str(refresh.access_token),
                            })
            else:
                if '@' in email_or_phone:
                    return Response("invalid email or password", status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response("invalid phone number or password", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('You are logged out', status=status.HTTP_204_NO_CONTENT)


class ChangePassword(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, query=None):
        return self.request.user
    
    def put(self, request):
        self.object = self.get_object()
        serializer = changePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response('Wrong old password', status=status.HTTP_400_BAD_REQUEST)
            # set new password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response('Password changed', status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

