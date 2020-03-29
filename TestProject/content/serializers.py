import os
import pytz
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from .models import File, Product, Subscription, Cart, Store

class ProductFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    ''' Show products of the owner's store '''

    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super(ProductFilteredPrimaryKeyRelatedField , self).get_queryset()
        if not request or not queryset:
            return None
        for q in queryset:
            if q.product_store.owner != request.user:
                queryset = queryset.exclude(id = q.id)
        return queryset

class FileUploadSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length = 30, style = {'placeholder' : 'please write your artibrary file name without its format'}, required = False)
    file_data = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf', 'avi', 'flv', 'wmv', 'mov', 'mp4', 'wma', 'flac', 'aac', 'mp3'])], required = True)
    file_price = serializers.IntegerField(style = {'placeholder' : 'if your file or your product which this file belongs to it, will be free you should not fill this field otherwise it will be ignored'}, required = False) 
    file_product = ProductFilteredPrimaryKeyRelatedField(queryset = Product.objects.all())
    is_free = serializers.BooleanField(required = True)
    file_id = serializers.SerializerMethodField('file_id_func')

    def file_id_func(self, obj):
        return obj.id
    
    def get_file(self, validated_data, should_rename, instance = None):
        file_data = self.context['request'].data.get('file_data')

        try:
            file_name = validated_data['file_name']
        except:
            file_name = str(file_data.name)
        else:
            if '.' in file_name:
                raise serializers.ValidationError(_('you should not have write file format in the name field'))
            should_rename = True

        try:
            file_price = validated_data['file_price']
        except:
            file_price = None

        file_product = validated_data['file_product']
        is_free = validated_data['is_free']

        if is_free or file_product.is_free:
            file_price = None
            is_free = True
        
        else:
            if not file_price:
                raise serializers.ValidationError(_('you should fill price or is_free field'))

        if not instance:
            file_obj = File(file_name = file_name, file_data = file_data, file_price = file_price, file_product = file_product, is_free = is_free)
            file_obj.save()

        if instance:
            File.objects.filter(pk=instance.id).update(file_name = file_name, file_data = file_data, file_price = file_price, file_product = file_product, is_free = is_free)

            file_obj = File.objects.get(pk = instance.id)

            if file_obj.file_data.path != instance.file_data.path:
                os.remove(instance.file_data.path)
                file_obj.file_data = file_data
                file_obj.save()

        return file_obj, should_rename
    
    def file_rename(self, file_obj, should_rename):
        ''' renaming a File if the owner gets a name ''' 

        if should_rename:
            initial_path = file_obj.file_data.path
            extension = os.path.splitext(file_obj.file_data.name)[1]
            file_obj.file_data.name = file_obj.file_name + extension
            new_path = settings.MEDIA_ROOT + '/' + file_obj.file_data.name
            os.rename(initial_path, new_path)
            file_obj.save()
        
        return file_obj
    
    def create(self , validated_data):
        ''' Create a new File ''' 

        should_rename = False
        returned_tuple = self.get_file(validated_data, should_rename)

        file_obj = self.file_rename(returned_tuple[0], returned_tuple[1])

        return file_obj

    def update(self, instance, validated_data):
        ''' Update File'''

        should_rename = False
        returned_tuple = self.get_file(validated_data, should_rename, instance)
        
        file_obj = self.file_rename(returned_tuple[0], returned_tuple[1])

        return file_obj

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ('buy_confirmation', )

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        exclude = ('buy_confirmation', )

class BuyProduct(serializers.Serializer):
    buy_choices = (('buy' , 'I want to buy this product') , 
                   ('cancel' , 'I want to cancel buying this product'))

    buy_confirmation = serializers.ChoiceField(choices = buy_choices)

class BuyFile(serializers.Serializer):
    buy_choices = (('buy' , 'I want to buy this file') , 
                   ('cancel' , 'I want to cancel buying this file'))

    buy_confirmation = serializers.ChoiceField(choices = buy_choices)

class BuySubscription(serializers.Serializer):
    buy_choices = (('buy' , 'I want to buy this subscription') , 
                   ('cancel' , 'I want to cancel buying this subscription'))

    buy_confirmation = serializers.ChoiceField(choices = buy_choices)

class Go_To_Buy_Step(serializers.Serializer):
    buy_choices = (('action' , 'I want to buy something'),)

    buy_confirmation = serializers.ChoiceField(choices = buy_choices)

class ShowProductSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name = 'show_product-detail',
    )

    class Meta:
        model = Product
        fields = ['url', 'product_name', 'is_free']

class ShowProductDetailSerializer(serializers.ModelSerializer):
    file_products = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='show_file-detail'
    )

    class Meta:
        model = Product
        fields = ['product_name', 'product_price', 'product_category', 'file_products']

class ShowFileSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name = 'show_file-detail',
    )

    class Meta:
        model = File
        fields = ['url', 'file_name', 'is_free']

class ShowFileDetailSerializer(serializers.ModelSerializer):
    file_data = serializers.SerializerMethodField()

    def check_subscription(self, cart_obj, file_obj):
        ''' check the validation of baught subscription ''' 

        utc=pytz.UTC

        try:
            sub_obj = cart_obj.baught_subscriptions.get(store_subscription = file_obj.file_product.product_store)
        except:
            return False
        else:
            now_datetime = datetime.now().replace(tzinfo=utc)
            unit = sub_obj.expiry_date_unit
            amount = sub_obj.expiry_date_amount

            if unit == 'day':
                expiry_date = cart_obj.date_of_buying_subscription + timedelta(days = amount)
                expiry_date = expiry_date.replace(tzinfo=utc)
            else:
                expiry_date = cart_obj.date_of_buying_subscription + timedelta(hours = amount)
                expiry_date = expiry_date.replace(tzinfo=utc)
            
            if now_datetime < expiry_date:
                return True
            else:
                return False

    def get_file_data(self, file_obj):
        ''' show the link of file to download it if the customer has the specific requirements ''' 

        request = self.context.get("request")

        if request.user != file_obj.file_product.product_store.owner and not file_obj.is_free:

            try:
                cart_obj = Cart.objects.get(user = request.user)
            except:
                return "to download this file, you should first pay for this file or buy its product"
            else:
                has_subscription = self.check_subscription(cart_obj, file_obj)

                ids_of_baught_products = cart_obj.baught_products
                ids_of_baught_products = cart_obj.baught_products

                if not ids_of_baught_products:
                    if file_obj.id not in ids_of_baught_files and not has_subscription:
                        return "to download this file, you should first pay for this file or buy its product"
                    else:
                        return request.build_absolute_uri(file_obj.file_data.url)
                   
                elif not ids_of_baught_files: 
                    if file_obj.file_product.id not in ids_of_baught_products and not has_subscription:
                        return "to download this file, you should first pay for this file or buy its product"
                    else:
                        return request.build_absolute_uri(file_obj.file_data.url)
                
                else:
                    if (file_obj.file_product.id not in ids_of_baught_products and file_obj.id not in ids_of_baught_files) and not has_subscription:
                        return "to download this file, you should first pay for this file or buy its product"
                    else:
                        return request.build_absolute_uri(file_obj.file_data.url)
        else:
            return request.build_absolute_uri(file_obj.file_data.url)


    class Meta:
        model = File
        fields = ['file_name', 'file_data', 'file_price']

class ShowMyCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        exclude = ('user', 'id')

class ShowSubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name = 'show_subscription-detail',
    )

    store_subscription = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='show_store-detail'
    )

    class Meta:
        model = Subscription
        fields = ['url', 'store_subscription']

class ShowSubscriptionDetailSerializer(serializers.ModelSerializer):
    expiry_date = serializers.SerializerMethodField('get_expiry_date')

    def get_expiry_date(self, sub_obj):
        return str(sub_obj.expiry_date_amount) + ' ' + sub_obj.expiry_date_unit

    class Meta:
        model = Subscription
        fields = ['amount', 'expiry_date']

class ShowStoreSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    subscription = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='show_subscription-detail'
    )

    products_store = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='show_product-detail'
    )

    def get_owner(self , store):
        return store.owner.username 

    class Meta:
        model = Store
        fields = ['products_store', 'subscription', 'owner']



