# views.py
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, ListAPIView
from django.contrib.auth import authenticate
from .serializers import (
    RoleSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ProductSerializer,
    CategorySerializer,
    OrderCreateSerializer,
    OrderSerializer,
    LogoutSerializer
)
from .models import Role, User, Product, Category, Order
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet  # Asegúrate de importar ModelViewSet

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        user = authenticate(email=email, password=password)

        if user:
            login_serializer = self.serializer_class(data=request.data)
            if login_serializer.is_valid():
                user_serializer = UserSerializer(user)
                return Response({
                    'token': login_serializer.validated_data['access'],
                    'refresh_token': login_serializer.validated_data['refresh'],
                    'user': user_serializer.data,
                    'message': 'Inicio de Sesión Exitoso'
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Contraseña o nombre de usuario incorrectos'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Contraseña o nombre de usuario incorrectos'}, status=status.HTTP_400_BAD_REQUEST)

class Logout(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        user = request.user  # Obtén el usuario autenticado directamente
        RefreshToken.for_user(user)  # Revoca el token del usuario
        return Response({'message': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)

# Ver los datos del usuario logueado
class UserView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# Actualizar los datos del usuario
class UpdateUserView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super(ProductViewSet, self).get_permissions()

# Crear órdenes con usuario autenticado
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save(id_user=request.user)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Ver lista de órdenes de usuario autenticado
class UserOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return Order.objects.filter(id_user=user_id)

class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

# Nueva vista para crear productos usando el formulario
class CreateProductView(APIView):
    permission_classes = [IsAdminUser]  # Solo usuarios administradores pueden crear productos

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)  # Usamos el serializador de productos
        if serializer.is_valid():
            product = serializer.save()  # Guardamos el producto
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
