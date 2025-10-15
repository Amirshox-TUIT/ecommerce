from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('added_at',)
    autocomplete_fields = ('product',)
    show_change_link = True


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'discount_percentage')
    autocomplete_fields = ('product',)
    show_change_link = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    inlines = [CartItemInline]
    autocomplete_fields = ('user',)

    def total_items(self, obj):
        return obj.items.count()
    total_items.short_description = 'Items count'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'user', 'status', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'phone')
    inlines = [OrderItemInline]
    autocomplete_fields = ('user',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('product__name', 'cart__user__username')
    autocomplete_fields = ('cart', 'product')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'discount_percentage')
    list_filter = ('discount_percentage',)
    search_fields = ('order__order_number', 'product__name')
    autocomplete_fields = ('order', 'product')
