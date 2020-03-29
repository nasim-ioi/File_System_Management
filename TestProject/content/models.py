from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator



class DateClass(models.Model):
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

class Category(DateClass):
    category_choices = (
        ("athletic" , "athletic"),
        ("educational" , "educational"),
        ("scientific" , "scientific"),
        ("political", "political"),
        ("cultural", "cultural"),
        ("historical", "historical")
    )
    category_name = models.CharField(max_length = 50 , choices = category_choices)

    def __str__(self):
        return self.category_name

class Store(DateClass):
    owner = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'owners', related_query_name = 'owner')

    def __str__(self):
        return self.owner.username+'-'+'Store'

class Product(DateClass):
    status_choices = (('buy' , 'buy') ,
                      ('cancel' , 'cancel'))

    product_name = models.CharField(max_length = 100)
    product_price = models.PositiveIntegerField(null = True, blank = True)
    is_free = models.BooleanField()
    product_category = models.ManyToManyField(Category, related_name = 'products_category', related_query_name = 'product_category')
    product_store = models.ForeignKey(Store, on_delete = models.CASCADE, related_name = 'products_store', related_query_name = 'product_store')
    buy_confirmation = models.CharField(max_length = 20 , choices = status_choices , default = 'cancel')

    def __str__(self):
        return self.product_name

class File(DateClass):
    status_choices = (('buy' , 'buy') ,
                      ('cancel' , 'cancel'))

    file_name = models.CharField(max_length = 30, null = True, blank = True)
    file_data = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf', 'avi', 'flv', 'wmv', 'mov', 'mp4', 'wma', 'flac', 'aac', 'mp3'])])
    file_product = models.ForeignKey(Product, on_delete = models.CASCADE, verbose_name = 'belonges_to_this_product', related_name = 'file_products', related_query_name = 'file_product')
    file_price = models.PositiveIntegerField(null = True, blank = True)
    is_free = models.BooleanField()
    buy_confirmation = models.CharField(max_length = 20 , choices = status_choices , default = 'cancel')

    def __str__(self):
        return self.file_name

class Subscription(DateClass):
    status_choices = (('buy' , 'buy') ,
                      ('cancel' , 'cancel'))
    
    expiry_date_unit_choices = (('day' , 'day') ,
                               ('hour' , 'hour'))

    amount = models.PositiveIntegerField()
    expiry_date_amount =  models.PositiveIntegerField()
    expiry_date_unit = models.CharField(max_length = 20 , choices = expiry_date_unit_choices)
    store_subscription = models.OneToOneField(Store, on_delete = models.CASCADE, related_name = 'subscription')
    buy_confirmation = models.CharField(max_length = 20 , choices = status_choices , default = 'cancel')
    
class Cart(DateClass):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'user_carts')
    baught_subscriptions = models.ManyToManyField(Subscription, related_name = 'carts', related_query_name = 'cart')
    date_of_buying_subscription = models.DateTimeField(null = True, blank = True)
    baught_products = ArrayField(models.PositiveSmallIntegerField(), null = True, blank = True)
    baught_files = ArrayField(models.PositiveSmallIntegerField(), null = True, blank = True)

    def __str__(self):
        return self.user.username+ '-' +'Cart'
    
    
