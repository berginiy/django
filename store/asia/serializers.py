from django.shortcuts import get_object_or_404
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated

from .models import Store, PurchasedProduct, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PurchasedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedProduct
        fields = ['user', 'product', 'quantity']

    def create(self, validated_data):
        user = validated_data.get('user')
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')

        purchased_product = PurchasedProduct.objects.create(user=user, product=product, quantity=quantity)

        request = self.context.get('request')
        if request:
            if 'cart' in request.session:
                request.session['cart'] = {}
                request.session.modified = True

        return purchased_product
