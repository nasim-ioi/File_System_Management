from django.contrib import admin
from .models import Category, Product, Store, File, Subscription, Cart


@admin.register(Category, Store)
class ShoppingAdmin(admin.ModelAdmin):
    readonly_fields = ['updated_date', 'created_date']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    exclude = ['buy_confirmation']
    readonly_fields = ['product_name', 'product_price', 'is_free', 'product_category',
                      'product_store', 'updated_date', 'created_date']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    exclude = ['buy_confirmation']
    readonly_fields = ['file_name', 'file_price', 'is_free','file_data', 
                      'file_product','updated_date', 'created_date']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    exclude = ['buy_confirmation']
    readonly_fields = ['amount', 'expiry_date_amount', 'expiry_date_unit',
                      'store_subscription','updated_date', 'created_date']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'baught_products', 'baught_files', 'baught_subscriptions',
                      'date_of_buying_subscription','updated_date', 'created_date']


