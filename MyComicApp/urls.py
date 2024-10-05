from django.urls import path, include
from rest_framework import routers
from MyComicApp import views
from rest_framework_simplejwt.views import TokenVerifyView

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'roles', views.RoleViewSet)

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'), 
    path('logout/', views.Logout.as_view(), name='logout'),
    
    path('', include(router.urls)),
    
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    path('user/', views.UserView.as_view(), name='user'),
    path('user/update/', views.UpdateUserView.as_view(), name='user_update'),
    path('orders/create/', views.CreateOrderView.as_view(), name='orders_create'),
    path('orders/user/', views.UserOrdersView.as_view(), name='orders_user_list'),
    
    # Ruta para crear un nuevo producto
    path('products/create/', views.CreateProductView.as_view(), name='create_product'),
]
