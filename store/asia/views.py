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

from .forms import RegisterUserForm, LoginUserForm
from .models import Store, Product, PurchasedProduct
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import PurchasedProductSerializer


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


def pageNotFound(request, exception):
    return render(request, 'asia/404.html', status=404)


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


from django.shortcuts import get_object_or_404, redirect
from .models import Product


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

    return redirect('cart')


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


class PurchaseCreateView(generics.CreateAPIView):
    queryset = PurchasedProduct.objects.all()
    serializer_class = PurchasedProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart = self.request.session.get('cart', {})

        if not cart:
            raise ValueError("Корзина пуста. Невозможно совершить покупку.")

        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            serializer.save(user=self.request.user.id, product=product.id, quantity=item['quantity'])

        self.request.session['cart'] = {}
        self.request.session.modified = True


from django.shortcuts import redirect


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
                'product': product.id,
                'quantity': item['quantity'],
            }
            serializer = PurchasedProductSerializer(data=purchased_data)

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
