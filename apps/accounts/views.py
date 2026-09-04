from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate,get_user_model
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .serializers import (
  RegisterSerializer,
  LoginSerializer,
  ForgotPasswordConfirmSerializer,
  ForgotPasswordRequestSerializer
)
from .models import ApprovalStatus
from rest_framework.permissions import IsAuthenticated
from .models import Profile
from .serializers import UpdateProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser # Add these parsers

User=get_user_model()

# Register View

class RegisterView(APIView):
  permission_classes=[]
  def post(self,request):
    serializer=RegisterSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(
        {"detail":"User registered successsfully"},
        status=status.HTTP_201_CREATED
      )
    return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# Login View
class LoginView(APIView):
  permission_classes=[]
  def post(self,request):
    serializer=LoginSerializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    email=serializer.validated_data['email'].lower()
    password=serializer.validated_data['password']
    # Authenticate against custom credentials
    user=authenticate(request,username=email,password=password)
    if not user:
      return Response({"detail":"Invalid credentials provided"},status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
      return Response({"detail":"This account has been deactivated"},status=status.HTTP_403_FORBIDDEN)
    if user.approval_status!=ApprovalStatus.APPROVED:
      return Response(
        {"detail":f"Access denied. Your account status is currently:{user.approval_status}"}
      )
    refresh=RefreshToken.for_user(user)
    return Response({
      "detail":"Login Successfull",
      "access":str(refresh.access_token),
      "refresh":str(refresh),
      "user":{
        "first_name":user.first_name,
        "last_name":user.last_name,
        "email":user.email,
        "role":user.role
      }

    },status=status.HTTP_200_OK)



class ForgotPasswordRequestView(APIView):
  permission_classes=[]
  def post(self,request):
    serializer=ForgotPasswordRequestSerializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    email=serializer.validated_data['email']
    user=User.objects.get(email=email)
    uid=urlsafe_base64_encode(force_bytes(user.pk))
    token=default_token_generator.make_token(user)
    reset_link = f"http://localhost:5173/reset-password?uid={uid}&token={token}"
    send_mail(
      subject="Reset your password",
      message=f"Please click the link below to safely configure your new password:\n\n{reset_link}",
      from_email=settings.DEFAULT_FROM_EMAIL, 
      recipient_list=[user.email],
      fail_silently=False
    )
    return Response({"detail":"password reset email link successfully dispatched"},status=status.HTTP_200_OK)


class ForgotPasswordConfirmView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Your new password has been successfully configured."}, 
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
  permission_classes=[IsAuthenticated]
  def get(self,request):
    profile,created=Profile.objects.get_or_create(user=request.user)
    serializer=UpdateProfileSerializer(profile)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
    )


class UpdateProfileView(APIView):
    permission_classes=[IsAuthenticated]
     # This allows your view to accept both text fields and file uploads from form-data
    parser_classes = [MultiPartParser, FormParser]
    def put(self,request):
      profile,created=Profile.objects.get_or_create(user=request.user)
      # pass the profile instance to the serializer
      serializer=UpdateProfileSerializer(profile,data=request.data,partial=True)
      if serializer.is_valid():
        serializer.save()
        return Response({
          "message":"Profile Updated Successfully",
          "user":serializer.data
        },
        status=status.HTTP_200_OK)
      return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
      )



      