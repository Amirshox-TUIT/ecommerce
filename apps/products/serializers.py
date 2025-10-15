from decimal import Decimal

from django.utils.text import slugify
from rest_framework import serializers

from apps.products.models import Product, Category, Brand, ProductImage
from apps.reviews.models import ProductReview


class InlineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class InlineBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'logo')


class ProductListSerializer(serializers.ModelSerializer):
    category = InlineCategorySerializer()
    brand = InlineBrandSerializer()
    final_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_final_price(self, obj):
        return Decimal(obj.price) * Decimal(1 - Decimal(obj.discount_percentage) / 100)

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        summa = 0
        count = 0
        for rating in obj.reviews.all():
            summa += rating.rating
            count += 1

        return summa / count if count else 0

    def get_primary_image(self, obj):
        for image in obj.images.all():
            if image.is_primary:
                return image.image_url
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all()
    )
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'slug':{'read_only':True},
            'id':{'read_only':True}}

    def validate_name(self, name):
        if len(name.strip()) < 1:
            raise serializers.ValidationError('Name can not be empty!')
        return name

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError('Price must be positive number!')
        return price

    def validate_stock_quantity(self, stock):
        if stock < 0:
            raise serializers.ValidationError('Stock quantity cannot be negative!')
        return stock

    def validate_discount_percentage(self, discount):
        if not (0 <= discount <= 100):
            raise serializers.ValidationError('Discount must be between 0 and 100')
        return discount

    def validate(self, attrs):
        category = attrs.get('category')
        brand = attrs.get('brand')
        if not category:
            raise serializers.ValidationError('Category doesnt exists')

        if not brand:
            raise serializers.ValidationError('Brand doesnt exists')

        return attrs

    def create(self, validated_data):
        name = validated_data.get('name')
        slug = slugify(name)
        return Product.objects.create(slug=slug, **validated_data)


class InlineImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class InlineReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'


class InlineProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price']


class ProductDetailSerializer(serializers.ModelSerializer):
    category = InlineCategorySerializer()
    brand = InlineBrandSerializer()
    images = InlineImagesSerializer(many=True, read_only=True)
    reviews = InlineReviewsSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_final_price(self, obj):
        return Decimal(obj.price) * Decimal((1 - Decimal(obj.discount_percentage) / 100))

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        summa = 0
        count = 0
        for rating in obj.reviews.all():
            summa += rating.rating
            count += 1

        return summa / count

    def get_related_products(self, obj):
        related = Product.objects.filter(category=obj.category).exclude(id=obj.id)[:5]
        return InlineProductSerializer(related, many=True).data


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock_quantity', 'discount_percentage', 'slug']

        extra_kwargs = {
            'slug':{'read_only':True},
        }

    def validate_name(self, name):
        if len(name.strip()) < 1:
            raise serializers.ValidationError('Name can not be empty!')
        return name

    def validate_price(self, price):
        if price < 0:
            raise serializers.ValidationError('Price must be positive number!')
        return price

    def validate_stock_quantity(self, stock):
        if stock < 0:
            raise serializers.ValidationError('Stock quantity cannot be negative!')
        return stock

    def validate_discount_percentage(self, discount):
        if not (0 <= discount <= 100):
            raise serializers.ValidationError('Discount must be between 0 and 100')
        return discount

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        instance.slug = slugify(name)
        instance.save()
        return instance


class ProductPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'slug':{'read_only':True},
        }

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Product name cannot be empty.")
        if len(value) < 3:
            raise serializers.ValidationError("Product name must be at least 3 characters long.")
        return value

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Product description must be at least 10 characters long.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        if value > 10_000_000:
            raise serializers.ValidationError("Price is too high (should not exceed 10,000,000).")
        return value

    def validate_discount_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount percentage must be between 0 and 100.")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        if 'name' in validated_data:
            instance.slug = slugify(validated_data['name'])

        instance.save()
        return instance















