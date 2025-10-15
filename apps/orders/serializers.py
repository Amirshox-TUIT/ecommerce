from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.orders.models import Cart, CartItem, Order
from apps.products.serializers import ProductListSerializer

User = get_user_model()


class InlineUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)


class InlineCartItems(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = '__all__'

    def get_sub_total(self, obj):
        return Decimal(obj.quantity) * Decimal(obj.product.price) * Decimal(1 - Decimal(obj.product.discount_percentage) / 100)


class CartViewSerializer(serializers.ModelSerializer):
    user = InlineUserSerializer(read_only=True)
    items = InlineCartItems(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = '__all__'

    def get_items_count(self, obj):
        return obj.items.count()

    def get_total_amount(self, obj):
        summ = Decimal(0)
        for item in obj.items.all():
            summ += Decimal(item.quantity) * Decimal(item.product.price) * Decimal(
                1 - Decimal(item.product.discount_percentage) / 100)
        return summ


class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        exclude = ('cart',)
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def validate_product(self, value):
        if not value.is_active:
            raise serializers.ValidationError('Product is bot exists')

        if value.stock_quantity <= 0:
            raise serializers.ValidationError('This product no in stock')
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be positive')
        return value


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'product': {'read_only': True},
            'added_at': {'read_only': True},
            'cart': {'read_only': True},
        }

        def validate_quantity(self, quantity):
            if quantity <= 0:
                raise serializers.ValidationError('Quantity must be positive')
            return quantity

        def validate(self, attrs):
            product = attrs.get('product')
            quantity = attrs.get('quantity')
            if product.stock_quantity < quantity:
                raise serializers.ValidationError('This product no in stock')
            return attrs


class OrderCreateSerializer(serializers.ModelSerializer):
    user = InlineUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'order_number': {'read_only': True},
            'status': {'read_only': True},
            'total_amount': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

        def validate_phone(self, phone):
            if not phone.startswith('+998') and not (6 < len(phone) < 15) and not phone[1:].isdigit():
                raise serializers.ValidationError('Invalid phone number')
            return phone

        def validate_shipping_address(self, address):
            if len(address.strip()) < 10:
                raise serializers.ValidationError('Address must have at least 10 characters')
            return address









