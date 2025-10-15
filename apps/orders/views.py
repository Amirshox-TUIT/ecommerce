from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response

from apps.orders.models import Cart, CartItem
from apps.orders.serializers import CartViewSerializer, CartItemCreateSerializer
from apps.products.models import Product


class CartRetrieveAPIView(GenericAPIView, RetrieveModelMixin):
    serializer_class = CartViewSerializer

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemCreateAPIView(GenericAPIView, CreateModelMixin):
    serializer_class = CartItemCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(user=user)

        product_id = self.request.data.get('product')
        quantity = int(self.request.data.get('quantity'))
        item = cart.items.filter(product_id=product_id).first()
        if item:
            item.quantity += quantity
            item.save()
        else:
            serializer.save(cart=cart)


class CartItemUpdateAPIView(GenericAPIView, UpdateModelMixin):
    serializer_class = CartItemCreateSerializer

    def get_queryset(self):
        return self.request.user.cart.items.all()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(cart=instance.cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemDeleteAPIView(GenericAPIView, DestroyModelMixin):
    def get_queryset(self):
        return self.request.user.cart.items.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCreateAPIView(GenericAPIView, CreateModelMixin):
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        cart = self.request.user.cart
        if not cart.items.all().exists():
            return Response({'detail': 'No items available'}, status=status.HTTP_404_NOT_FOUND)

        if not all(item.quantity for item in cart.items.all()):
            return Response({'detail': 'No items available'}, status=status.HTTP_404_NOT_FOUND)











