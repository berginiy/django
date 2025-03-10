from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Store, Product, PurchasedProduct


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'title', 'slug', 'time_create', 'time_update', 'is_published']


class ProductSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'image', 'slug', 'time_create', 'is_published', 'store']


class PurchasedProductSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product',
                                                    write_only=True)  # Новое поле для записи ID продукта

    class Meta:
        model = PurchasedProduct
        fields = ['id', 'user', 'product', 'product_id', 'quantity', 'purchase_date']

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data.get('product')  # Теперь это будет объект Product
        quantity = validated_data.get('quantity')

        purchased_product = PurchasedProduct.objects.create(user=user, product=product, quantity=quantity)

        request = self.context.get('request')
        if request:
            if 'cart' in request.session:
                request.session['cart'] = {}
                request.session.modified = True

        return purchased_product


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    title = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
