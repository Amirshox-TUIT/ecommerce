from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products import serializers
from apps.products.models import Product
from apps.products.serializers import ProductCreateSerializer, ProductDetailSerializer, ProductUpdateSerializer, \
    ProductPartialUpdateSerializer


class ProductListAPIView(APIView):
    serializer_class = serializers.ProductListSerializer
    model = Product

    def get(self, request):
        cat_id = request.query_params.get('cat_id')
        brand_id = request.query_params.get('brand_id')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        is_featured = request.query_params.get('is_featured')
        s = request.query_params.get('s')
        products = self.model.objects.filter(is_active=True)

        if cat_id:
            products = self.model.objects.filter(cat_id=cat_id)

        if brand_id:
            products = self.model.objects.filter(brand_id=brand_id)

        if min_price:
            products = self.model.objects.filter(price__gte=min_price)

        if max_price:
            products = self.model.objects.filter(price__lte=max_price)

        if is_featured:
            products = self.model.objects.filter(is_featured=is_featured)

        if s:
            products = self.model.objects.filter(Q(name__icontains=s) | Q(description__icontains=s))

        if not products.exists():
            return Response(data={'message':'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductCreateAPIView(APIView):
    serializer_class = ProductCreateSerializer
    model = Product

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data={'message':'Data is incorrect'}, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    serializer_class = ProductDetailSerializer
    def get(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(data={'message':'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(product)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductPutAPIView(APIView):
    serializer_class = ProductUpdateSerializer
    model = Product

    def put(self, request, pk):
        try:
            product = self.model.objects.get(id=pk)
        except self.model.DoesNotExist:
            return Response(data={'message':'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data={'message':'Data is incorrect'}, status=status.HTTP_400_BAD_REQUEST)


class ProductPatchAPIView(APIView):
    serializer_class = ProductPartialUpdateSerializer
    model = Product

    def patch(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(data={'message':'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data={'message':'Data is incorrect'}, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(data={'message':'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        product.is_active = False
        product.save()
        return Response(data={'message':'Product delete successfully'}, status=status.HTTP_204_NO_CONTENT)




