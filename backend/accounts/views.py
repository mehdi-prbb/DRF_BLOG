from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserRegisterSerializer

class UserRegister(APIView):
    """
    Register new users using phone number and password.
    """

    def post(self, request):
        ser_data = UserRegisterSerializer(data=request.data)
        
        if ser_data.is_valid():
            ser_data.create(ser_data.validated_data)
            return Response(ser_data.data, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)
