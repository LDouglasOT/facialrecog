from django.db import models
from django.db import models
from django.utils.timezone import now
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models


# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone Number field must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []  

    def __str__(self):
        return self.phone_number




class Face(models.Model):
    name = models.CharField(max_length=255)
    embedding = models.BinaryField() 
    faceId = models.UUIDField(editable=True, default=uuid.uuid4, unique=True)


class Form(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    classteachernames = models.CharField(max_length=255)
    classteacherphone = models.CharField(max_length=20)
    classdirections = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default="Parent")
    phone = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    imgurl = models.URLField(blank=True, null=True)
    residence = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    isBanned = models.BooleanField(default=False)

class Child(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    fees = models.IntegerField(default=0)
    paycode = models.CharField(max_length=100)
    classname = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='children')
    paid = models.IntegerField(default=0)
    expected_fees = models.IntegerField(default=0)

class Staff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    imgurl = models.URLField(blank=True, null=True)

class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateTimeField()
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='attendances')
    checkintype = models.CharField(max_length=50, default="face")
    studentcontact = models.CharField(max_length=50, default="parent")
    reason = models.TextField()
    present = models.BooleanField()
    time_in = models.DateTimeField(default=now)
    time_out = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Pledge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='pledges')
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(default=now)
    days = models.IntegerField()
# 07
class ClearanceCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100)
    visitor = models.CharField(max_length=255)
    reason = models.CharField(max_length=255, default="fees payment and reconciliation")
    contact = models.CharField(max_length=20)
    visitor_contact = models.CharField(max_length=20, blank=True, null=True)
    relationship = models.CharField(max_length=255)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='codes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    creator = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    paycode = models.CharField(max_length=100)
    student_name = models.CharField(max_length=255)
    parent_name = models.CharField(max_length=255)
    parent_phone = models.CharField(max_length=20)
    transaction_reference = models.CharField(max_length=255)
    mno_transaction_reference_id = models.CharField(max_length=255)
    issued_receipt_number = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(default=now)
    days = models.IntegerField()



class Product(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  ProductName = models.CharField(max_length=250)
  price = models.IntegerField(default=0)
  quantity = models.IntegerField(default=0)
  itemDescription = models.CharField(max_length=250)
  images = models.JSONField; 
  Type = models.CharField(max_length=250)
  imgurl = models.CharField(max_length=250)
  venue = models.CharField(max_length=250)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="products")
    quantity = models.IntegerField(default=0)
    parent = models.ForeignKey(Parent,on_delete=models.CASCADE,related_name="parent")
    created_at = models.DateField(auto_now_add=True)
    paid = models.IntegerField(default=0)
    fulfilled = models.BooleanField(default=False)