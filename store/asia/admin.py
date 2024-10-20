from django.contrib import admin
from .models import Store, Product, PurchasedProduct


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'time_create', 'is_published')
    list_filter = ('is_published', 'time_create')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'store', 'is_published')
    list_filter = ('is_published', 'store')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}


@admin.register(PurchasedProduct)
class PurchasedProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'purchase_date')
