from collections import defaultdict
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import RegisterUserForm, LoginUserForm
from .models import Store, Product, PurchasedProduct
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, StoreSerializer, ProductSerializer, PurchasedProductSerializer, CartSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Старые представления
class Home(ListView):
    model = Store
    template_name = 'asia/index.html'
    context_object_name = 'stores'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Главная страница"
        return context

    def get_queryset(self):
        return Store.objects.filter(is_published=True)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'asia/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Регистрация"
        return context


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'asia/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Авторизация"
        return context

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('home')


def pageNotFound(request, exception):
    return render(request, 'asia/404.html', status=404)


def store_list(request):
    products = Product.objects.all()
    return render(request, 'asia/store_list.html', {'products': products})


def store_list_category(request, store_slug=None):
    categories = Store.objects.all()

    if store_slug:
        selected_store = get_object_or_404(Store, slug=store_slug)
        products = selected_store.products.all()
    else:
        products = Product.objects.all()[:3]

    return render(request, 'asia/store_list_category.html', {'categories': categories, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'asia/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'title': product.title,
            'price': str(product.price),
            'quantity': 1
        }

    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f'Товар "{product.title}" добавлен в корзину!')
    referer = request.META.get('HTTP_REFERER', 'home')
    return redirect(referer)


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []

    if cart:
        for item_id, item_info in cart.items():
            cart_items.append({
                'title': item_info['title'],
                'price': item_info['price'],
                'quantity': item_info['quantity']
            })

    return render(request, 'asia/cart.html', {'cart_items': cart_items})


def confirm_purchase(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        user = request.user

        if not cart:
            return JsonResponse({'message': 'Корзина пуста'}, status=400)

        for item_id, item in cart.items():
            product = get_object_or_404(Product, id=item_id)
            purchased_data = {
                'user': user.id,
                'product_id': product.id,
                'quantity': item['quantity'],
            }
            serializer = PurchasedProductSerializer(data=purchased_data, context={'request': request})

            if serializer.is_valid():
                serializer.save()
            else:
                return JsonResponse({'message': f'Ошибка валидации: {serializer.errors}'}, status=400)

        request.session['cart'] = {}
        request.session.modified = True

        return redirect('home')

    return JsonResponse({'message': 'Метод не разрешен'}, status=405)


def purchase_success(request):
    purchased_items = PurchasedProduct.objects.filter(user=request.user).order_by('-id')
    return render(request, 'asia/purchase_success.html', {'purchased_items': purchased_items})


def iphone15(request):
    product = get_object_or_404(Product, slug="iphone-15")
    return render(request, 'asia/iphone15.html', {'product': product})


def iphone15pro(request):
    product = get_object_or_404(Product, slug="iphone-15-pro")
    return render(request, 'asia/iphone15pro.html', {'product': product})


def iphone15promax(request):
    product = get_object_or_404(Product, slug="iphone-15-pro-max")
    return render(request, 'asia/iphone15promax.html', {'product': product})


def purchase_history(request):
    if request.user.is_authenticated:
        purchased_items = PurchasedProduct.objects.filter(user=request.user).order_by('-purchase_date')
        return render(request, 'asia/purchase_history.html', {'purchased_items': purchased_items})
    else:
        return redirect('login')


# Новые API-эндпоинты
class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="Получить список всех пользователей (только для админов)",
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CurrentUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить информацию о текущем пользователе",
        responses={200: UserSerializer()}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class StoreListAPIView(generics.ListAPIView):
    queryset = Store.objects.filter(is_published=True)
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Получить список всех опубликованных категорий",
        responses={200: StoreSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StoreDetailAPIView(generics.RetrieveAPIView):
    queryset = Store.objects.filter(is_published=True)
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @swagger_auto_schema(
        operation_description="Получить информацию о категории по её slug",
        responses={200: StoreSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(is_published=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Получить список всех опубликованных товаров",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_published=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @swagger_auto_schema(
        operation_description="Получить информацию о товаре по его slug",
        responses={200: ProductSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PurchasedProductListAPIView(generics.ListAPIView):
    serializer_class = PurchasedProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchasedProduct.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить список купленных товаров текущего пользователя",
        responses={200: PurchasedProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PurchaseCreateView(generics.CreateAPIView):
    queryset = PurchasedProduct.objects.all()
    serializer_class = PurchasedProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создание записи о покупке. Очищает корзину после успешного выполнения.",
        request_body=PurchasedProductSerializer,
        responses={
            201: "Покупка успешно создана",
            400: "Ошибка валидации или пустая корзина",
        }
    )
    def perform_create(self, serializer):
        cart = self.request.session.get('cart', {})
        if not cart:
            raise ValueError("Корзина пуста. Невозможно совершить покупку.")
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            serializer.save(user=self.request.user, product=product, quantity=item['quantity'])
        self.request.session['cart'] = {}
        self.request.session.modified = True


class CartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить содержимое корзины текущего пользователя",
        responses={200: CartSerializer()}
    )
    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = [
            {
                'product_id': int(product_id),
                'title': item['title'],
                'price': item['price'],
                'quantity': item['quantity']
            }
            for product_id, item in cart.items()
        ]
        serializer = CartSerializer({'items': cart_items})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Добавить товар в корзину",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID товара'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество', default=1),
            },
            required=['product_id']
        ),
        responses={200: "Товар добавлен в корзину"}
    )
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += int(quantity)
        else:
            cart[str(product_id)] = {
                'title': product.title,
                'price': str(product.price),
                'quantity': int(quantity)
            }

        request.session['cart'] = cart
        request.session.modified = True
        return Response({"message": f"Товар {product.title} добавлен в корзину"})
