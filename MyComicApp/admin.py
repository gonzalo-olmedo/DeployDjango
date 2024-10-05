from django.contrib import admin
from django.utils.html import format_html
from .models import User, Role, Category, Product, Order, OrderItem  # Asegúrate de incluir todos tus modelos aquí.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Users Admin
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'address', 'image', 'display_orders', 'role')
    filter_horizontal = ('user_permissions',)

    def display_orders(self, obj):
        return ", ".join([str(order.id_order) for order in obj.orders.all()])
    
    display_orders.short_description = 'Orders'
    
    def has_add_permission(self, request):
        return not request.user.groups.filter(name='Vendedor').exists()

    def has_change_permission(self, request, obj=None):
        return not request.user.groups.filter(name='Vendedor').exists()

    def has_delete_permission(self, request, obj=None):
        return not request.user.groups.filter(name='Vendedor').exists()

    def has_view_permission(self, request, obj=None):
        return request.user.groups.filter(name='Vendedor').exists() or super().has_view_permission(request, obj)

admin.site.register(User, UserAdmin)

# Role Admin
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id_role', 'name')

admin.site.register(Role, RoleAdmin)

# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id_category', 'name')

admin.site.register(Category, CategoryAdmin)

# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id_product', 'name', 'price', 'stock', 'image_tag')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"

    image_tag.short_description = 'Image'

admin.site.register(Product, ProductAdmin)

# Order Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id_order', 'id_user', 'state', 'order_date', 'payment_method', 'shipping_method', 'payment_status', 'total_amount')
    list_filter = ('state', 'order_date', 'payment_method', 'shipping_method', 'payment_status')
    search_fields = ('id_order', 'id_user__email')
    inlines = [OrderItemInline]

    def order_items(self, obj):
        return ", ".join([str(item) for item in obj.order_items.all()])
    
    order_items.short_description = 'Order Items'

    def has_view_permission(self, request, obj=None):
        return request.user.groups.filter(name='Vendedor').exists() or super().has_view_permission(request, obj)

admin.site.register(Order, OrderAdmin)
