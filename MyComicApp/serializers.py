# mycomicapp/serializers.py

from rest_framework import serializers
from .models import Role, User, Product, Category, Order, OrderItem
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from decimal import Decimal
from django.utils import timezone
import cloudinary
import cloudinary.uploader


# 1. User Serializer
class UserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'address', 'phone', 'image']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            address=validated_data['address'],
            phone=validated_data['phone'],
            image=image  # CloudinaryField manejará la subida
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name  = validated_data.get('last_name', instance.last_name)
        instance.address     = validated_data.get('address', instance.address)
        instance.phone       = validated_data.get('phone', instance.phone)
        image = validated_data.get('image', instance.image)
        if image:
            instance.image = image

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance

# 5. Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = '__all__'

    def validate_image(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB
                raise serializers.ValidationError("La imagen es demasiado grande (máximo 5MB).")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("Solo se permiten imágenes.")
        return value

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        if image:
            upload_result = cloudinary.uploader.upload(image)
            validated_data['image'] = upload_result['secure_url']  # Almacena la URL de la imagen

        product = Product.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):
        # Actualizar otros campos del producto
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.pages = validated_data.get('pages', instance.pages)
        instance.format = validated_data.get('format', instance.format)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.isbn = validated_data.get('isbn', instance.isbn)

        instance.category = validated_data.get('category', instance.category)

        new_image = validated_data.get('image', None)
        if new_image:
            upload_result = cloudinary.uploader.upload(new_image)
            instance.image = upload_result['secure_url']  # Almacena la nueva URL de la imagen

        instance.save()  # Guardar los cambios
        return instance

# El resto de los serializers permanecen sin cambios
class LogoutSerializer(serializers.Serializer):
    user = serializers.IntegerField()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

# Order Serializer---> Order Items Serializer 
class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderCreateSerializer(serializers.ModelSerializer):
    order_items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['state', 'payment_method', 'shipping_method', 'payment_status', 'total_amount', 'order_items']

    def validate(self, attrs):
        order_items_data = attrs.get('order_items', [])
        for order_item_data in order_items_data:
            if 'product' not in order_item_data:
                raise serializers.ValidationError("Cada elemento de 'order_items' debe tener una clave 'product'.")
            product = order_item_data['product']
            quantity = order_item_data['quantity']
            if product.stock < quantity:
                raise serializers.ValidationError(f"No hay suficiente stock para {product.name}")
        attrs.setdefault('state', 'En proceso')
        attrs.setdefault('order_date', timezone.now().date())
        attrs.setdefault('payment_method', 'credit_card')
        attrs.setdefault('shipping_method', 'express')
        attrs.setdefault('payment_status', 'pagado')
        return attrs

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        total_amount = Decimal(0)

        for order_item_data in order_items_data:
            product = order_item_data['product']
            quantity = order_item_data['quantity']
            subtotal = product.price * quantity
            total_amount += subtotal

            # Actualizar el stock del producto
            product.stock -= quantity
            product.save()

        validated_data['total_amount'] = total_amount
        order = Order.objects.create(**validated_data)

        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)

        return order

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['id_order_items', 'product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id_order', 'user', 'state', 'order_date', 'payment_method', 'shipping_method', 'payment_status', 'total_amount', 'order_items']
