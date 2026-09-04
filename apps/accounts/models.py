from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.core.validators import RegexValidator
from .managers import UserManager
phone_regex = RegexValidator(
    regex=r'^(?:\+?977[- ]?)?(?:9[78]\d{8}|0\d{2}[- ]?\d{6}|01[- ]?\d{7})$',
    message="Phone number must be a valid Nepali mobile (10 digits starting with 97/98) or landline number. Country code (+977) is optional."
)


class Role(models.TextChoices):
  ADMIN="ADMIN","admin"
  SELLER="SELLER","seller"
  BUYER="BUYER","buyer"


class ApprovalStatus(models.TextChoices):
  PENDING="PENDING","pending"
  APPROVED="APPROVED","approved"
  REJECTED="REJECTED","rejected"

class User(AbstractBaseUser,PermissionsMixin):
  first_name=models.CharField(max_length=100)
  last_name=models.CharField(max_length=100)
  email=models.EmailField(unique=True)
  phone_regex = RegexValidator(
    regex=r'^(?:\+?977[- ]?)?(?:9[78]\d{8}|0\d{2}[- ]?\d{6}|01[- ]?\d{7})$',
    message="Phone number must be a valid Nepali mobile (10 digits starting with 97/98) or landline number. Country code (+977) is optional."
)
  phone=models.CharField(validators=[phone_regex],max_length=17,blank=True)
  role=models.CharField(max_length=20,choices=Role.choices,default=Role.BUYER)
  approval_status=models.CharField(max_length=20,choices=ApprovalStatus.choices,default=ApprovalStatus.PENDING)
  profile_image=models.ImageField(upload_to="profiles/",blank=True,null=True)
  is_active=models.BooleanField(default=True)
  is_staff=models.BooleanField(default=False)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  objects=UserManager()
  USERNAME_FIELD="email"
  REQUIRED_FIELDS=["first_name","last_name"]
  def __str__(self):
    return f"{self.email} ({self.role})"
  def save(self,*args,**kwargs):
     # Auto-approve Buyers, force Sellers/Admins to go through approval process
     if not self.pk and self.role==Role.BUYER:
       self.approval_status=ApprovalStatus.APPROVED
     super().save(*args,**kwargs)

class Profile(models.Model):
  user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
  phone=models.CharField(validators=[phone_regex],max_length=15,blank=True,null=True)
  profile_image=models.ImageField(upload_to="profile_images/",blank=True,null=True)
  address=models.CharField(max_length=255,blank=True,null=True)
  def __str__(self):
    return f"{self.user.email}'s Profile"