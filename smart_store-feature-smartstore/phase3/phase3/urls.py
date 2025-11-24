"""
URL configuration for phase3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include
from . import views

urlpatterns = [
    path('', views.default, name='default'),
    path('admin/', admin.site.urls),
#  path('', views.fridge_dashboard, name='default'),   
    path('products/', views.products_page, name='products_page'),
    path('checkout/', views.checkout, name='checkout_api'),

    path('customers/create/', views.create_customer_page, name='create_customer_page'),
    path('products/create/', views.create_product_page, name='create_product_page'),
    path('inventory/add/', views.add_inventory_page, name='add_inventory_page'),
    path('customers/', views.customers_page, name='customers_page'),
    path('inventory/', views.inventory_page, name='inventory_page'),
    path('receipts/', views.receipts_page, name='receipts_page'),
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout_page, name='logout_page'),
    path('dashboard/', views.dashboard_page, name='dashboard_page'),
    path('i18n/', include('django.conf.urls.i18n')),

]