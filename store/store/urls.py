"""
URL configuration for store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from asia import views
from asia.views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Интернет-магазина",
        default_version='v1',
        description="Документация API для интернет-магазина на Django",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Home.as_view(), name='home'),
    path('register/', views.RegisterUser.as_view(), name='register'),  # Исправлено
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('store/', views.store_list, name='store_list'),
    path('store_category/<slug:store_slug>/', views.store_list_category, name='store_list_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('confirm_purchase/', views.confirm_purchase, name='confirm_purchase'),
    path('purchase_success/', views.purchase_success, name='purchase_success'),
    path('iphone15/', views.iphone15, name='iphone15'),
    path('iphone15pro/', views.iphone15pro, name='iphone15pro'),
    path('iphone15promax/', views.iphone15promax, name='iphone15promax'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('purchase-history/', views.purchase_history, name='purchase_history'),
    path('', include('social_django.urls', namespace='social')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/users/', views.UserListAPIView.as_view(), name='user-list'),
    path('api/users/me/', views.CurrentUserAPIView.as_view(), name='current-user'),
    path('api/stores/', views.StoreListAPIView.as_view(), name='store-list'),
    path('api/stores/<slug:slug>/', views.StoreDetailAPIView.as_view(), name='store-detail'),
    path('api/products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('api/products/<slug:slug>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('api/purchases/', views.PurchasedProductListAPIView.as_view(), name='purchased-product-list'),
    path('api/purchase/', views.PurchaseCreateView.as_view(), name='purchase'),
    path('api/cart/', views.CartAPIView.as_view(), name='cart-api'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = views.pageNotFound
