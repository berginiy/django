from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy

class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['site_name'] = settings.SITE_NAME
        context['site_url'] = get_current_site(self.request).domain
        context['login_url'] = reverse_lazy('login')
        context['register_url'] = reverse_lazy('register')
        return context
