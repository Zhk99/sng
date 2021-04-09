
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from .verify import send_user_activation_email, activation_user, send_sms_code
from . import serializers


# Create your views here.
class LoginView(APIView):

    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'id': user.id, 'email': user.email,
                         'token': token.key}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        return Response({'success': "Successfully logged out"}, status=status.HTTP_200_OK)


class UserRegistrationView(APIView):

    serializer_class = serializers.UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_user_activation_email(user, request.data.get('email'))
            send_sms_code(request)
            return Response({'message': 'Please confirm your email address or get sms code'
                                        ' to complete the registration'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivationUserView(APIView):

    def get(self, request, uidb64, token):
        return activation_user(uidb64, token)


class ActivationUserNumber(APIView):
    
    def get(self, request, sms_code):
        code = int(sms_code)
        if request.user.authenticate(code):
            phone = request.user.is_active
            phone.verified = True
            phone.save()
            return Response(dict(detail="Phone number verified successfully"), status=201)
        return Response(dict(detail='The provided code did not match or has expired'), status=200)
