from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from .models import Role,ApprovalStatus
from .validators import phone_regex
from .models import Profile
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken,TokenError
from rest_framework import status
from rest_framework.response import Response

User=get_user_model()

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,required=True,validators=[validate_password])
    password_confirm=serializers.CharField(write_only=True)
    class Meta:
      model=User
      fields=['first_name','last_name','email','phone','role','password','password_confirm']

    def validate(self,attrs):
      if attrs['password']!=attrs['password_confirm']:
        raise serializers.ValidationError({"password":"Passwords do not match"})
      if attrs.get('role')==Role.ADMIN:
        raise serializers.ValidationError({"role":"Cannot register directly as an admin"})
      return attrs

    def create(self,validated_data):
     validated_data.pop('password_confirm',None)
     return User.objects.create_user(**validated_data)



class LoginSerializer(serializers.Serializer):
 email=serializers.EmailField()
 password=serializers.CharField(write_only=True)



# Forgot Password Request
class ForgotPasswordRequestSerializer(serializers.Serializer):
 email=serializers.EmailField()
 def validate_email(self,value):
  normalized_email=value.lower()
  if not User.objects.filter(email=normalized_email).exists():
   raise serializers.ValidationError("If an account exists for this email, a password reset link has been sent.")
  return normalized_email


# Forgot Password Confirm
class ForgotPasswordConfirmSerializer(serializers.Serializer):
 uid=serializers.CharField()
 token=serializers.CharField()
 new_password=serializers.CharField(write_only=True,validators=[validate_password])
 def validate(self,attrs):
  try:
   uid=force_str(urlsafe_base64_decode(attrs['uid']))
   user=User.objects.get(pk=uid)
  except (TypeError,ValueError,OverflowError,User.DoesNotExist):
   raise serializers.ValidationError({"link":"This link is malformed or invalid"})
  # Cryptographically check if the link belongs to this user and hasn't expired
  if not default_token_generator.check_token(user,attrs['token']):
   raise serializers.ValidationError({"link":"This password reset link has expired or already has been used"})
  attrs['user']=user
  return attrs

 def save(self):
  user=self.validated_data['user']
  user.set_password(self.validated_data['new_password'])
  user.save()
  return user


class UpdateProfileSerializer(serializers.ModelSerializer):
 first_name=serializers.CharField(source="user.first_name",required=False,allow_blank=True)
 last_name=serializers.CharField(source="user.last_name",required=False,allow_blank=True)
 email=serializers.EmailField(source="user.email",required=False)
 phone=serializers.CharField(source="user.phone",validators=[phone_regex],required=False,allow_blank=True)
 class Meta:
  model=Profile
  fields=[
   "first_name",
   "last_name",
   "email",
   "phone",
   "profile_image",
   "address"
  ]
 def validate_email(self,value):
   user=self.instance.user
   lower_email=value.lower()
   if User.objects.filter(email=lower_email).exclude(id=user.id).exists():
    raise serializers.ValidationError("This email is already in use")
   return lower_email

 def update(self,instance,validated_data):
  #  Extract nested user data(first name,last name,email)
    user_data=validated_data.pop('user',{})
    user=instance.user
    for attr,value in user_data.items():
     setattr(user,attr,value)
    user.save

    # update the profile fields(phone,profile_image,address)
    for attr,value in validated_data.items():
     setattr(instance,attr,value)
    instance.save()
    return instance


class CustomTokenRefreshView(TokenRefreshView):
 
 def post(self,request,*args,**kwargs):
  permission_classes=[]
  def post(self,request,*args,**kwargs):
   serializer=self.get_serializer(data=request.data)
   try:
    serializer.is_valid(raise_exception=True)
   except TokenError as e:
    raise InvalidToken(e.args[0])
   token_data=serializer.validated_data
   return Response({
    "detail":"Tokens refreshed successfully",
    "access":token_data.get("access"),
    "refresh":token_data.get("refresh")
   },status=status.HTTP_200_OK)