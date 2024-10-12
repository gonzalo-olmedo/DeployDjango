from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group 
import cloudinary
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .utils import generate_public_id

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, role=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, role, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True) 
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    address = models.CharField(max_length=255, default='', blank=False)
    phone = models.CharField(max_length=20, default='', blank=False)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, default=1, related_name='users')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    def user_orders(self):
        return Order.objects.filter(id_user=self)
    
    
    class Meta:
        db_table = 'mycomicapp_user'

class Role(models.Model):
    id_role = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name

class Category(models.Model):
    id_category = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name    


class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=5000, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    discount = models.IntegerField(blank=True, null=True)
    stock = models.IntegerField(blank=False)
    image = CloudinaryField('image', blank=True, null=True)  
    pages = models.IntegerField(blank=True, null=True)
    format = models.CharField(max_length=45, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    isbn = models.CharField(max_length=45, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    calification = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('5.0'))
        ]
    )

    class Meta: 
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.image:
            public_id = generate_public_id(self, self.image.name)

            try:
                # Subir la imagen a Cloudinary
                upload_result = cloudinary.uploader.upload(self.image, public_id=public_id)

                # Asignar la URL de la imagen a self.image
                self.image = upload_result['secure_url']
            except Exception as e:
                print(f"Error al subir la imagen a Cloudinary: {e}")  # Esto te ayudará a ver qué está fallando
                raise  # Lanza el error nuevamente después de imprimirlo

        super().save(*args, **kwargs)




class Order(models.Model):
    id_order = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='user_id', related_name='orders')
    state = models.CharField(max_length=45, blank=True)
    order_date = models.DateField(null=True)
    payment_method = models.CharField(max_length=45, blank=True)
    shipping_method = models.CharField(max_length=45, null=True)
    payment_status = models.CharField(max_length=45, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order {self.id_order}'


class OrderItem(models.Model):
    id_order_items = models.AutoField(primary_key=True)
    quantity = models.IntegerField(blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='order_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        
    def __str__(self):
        return f'{self.quantity} of {self.product.name} in Order {self.order.id_order}'