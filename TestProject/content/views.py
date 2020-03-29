from os import remove
import pytz
from datetime import datetime, timedelta
from django.shortcuts import render

from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.renderers import MultiPartRenderer
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework import permissions

from .models import File, Product, Subscription, Cart, Store
from .serializers import (FileUploadSerializer, ProductSerializer, SubscriptionSerializer,
                         ShowProductSerializer, ShowFileSerializer, ShowProductDetailSerializer,
                         ShowFileDetailSerializer, ShowMyCartSerializer, ShowSubscriptionSerializer,
                         ShowSubscriptionDetailSerializer, Go_To_Buy_Step, BuyProduct, BuyFile, 
                         BuySubscription, ShowStoreSerializer,)


class IsOwnerUser(permissions.BasePermission):
    ''' check the user is owner or not ''' 

    def has_permission(self, request, view):
        try:
            if request.user.profiles.is_owner:
                return True
            else:
                return False
        except:
            return False

class FileUploadViewSet(ModelViewSet):
    ''' owner can upload file to his/her store ''' 

    permission_classes = [IsAuthenticated , IsOwnerUser]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        query = File.objects.all()
    
        for q in query:
            if q.file_product.product_store.owner != self.request.user:
                query = query.exclude(id = q.id)
        return query

    serializer_class = FileUploadSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        remove(instance.file_data.path)
        self.perform_destroy(instance)
        return Response(status = HTTP_204_NO_CONTENT)

class ProductViewSet(ModelViewSet):
    ''' owner can add product to his/her store ''' 

    permission_classes = [IsAuthenticated , IsOwnerUser]

    def get_queryset(self):
        query = Product.objects.all()
    
        for q in query:
            if q.product_store.owner != self.request.user:
                query = query.exclude(id = q.id)
        return query

    serializer_class = ProductSerializer

class SubscriptionViewSet(ModelViewSet):
    ''' owner can add subscription to his/her store ''' 

    permission_classes = [IsAuthenticated , IsOwnerUser]

    def get_queryset(self):
        query = Subscription.objects.all()
    
        for q in query:
            if q.store_subscription.owner != self.request.user:
                query = query.exclude(id = q.id)
        return query

    serializer_class = SubscriptionSerializer

class ShowProductViewSet(ModelViewSet):
    ''' users can see products and buy them ''' 

    permission_classes = [IsAuthenticated]

    queryset = Product.objects.all()

    serializers = {
        'list' : ShowProductSerializer,
        'retrieve' : ShowProductDetailSerializer,
        'create' : Go_To_Buy_Step,
        'update' : BuyProduct,
        'partial_update' : BuyProduct
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action)
    
    def create(self , request):
        return Response("Please select an exact product to buy")

    def update(self, request, *args, **kwargs):
            product_obj = Product.objects.get(pk = int(kwargs['pk']))
            cart_tuple = Cart.objects.get_or_create(user = request.user)
            cart_obj = cart_tuple[0]

            if request.data['buy_confirmation'] == 'buy':
                if not cart_obj.baught_products:
                    cart_obj.baught_products = []
                
                if product_obj.id not in cart_obj.baught_products:
                    cart_obj.baught_products.append(product_obj.id)
                    cart_obj.save()
                else:
                    return Response("You have already baught this product")

                return Response("You baught this product successfully")

            else:
                if product_obj.id not in cart_obj.baught_products:
                    return Response("You canceled buying this product")
                else:
                    return Response("You have already baught this product")
    
    def partial_update(self, request, *args, **kwargs):
        return None

    def destroy(self, request, *args, **kwargs):
        return Response("You do not have the permission to delete this product")

class ShowFileViewSet(ModelViewSet):
    ''' users can see files and buy or download them ''' 

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    queryset = File.objects.all()

    serializers = {
        'list' : ShowFileSerializer,
        'retrieve' : ShowFileDetailSerializer,
        'create' : Go_To_Buy_Step,
        'update' : BuyFile,
        'partial_update' : BuyFile
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action)
    
    def create(self , request):
        return Response("Please select an exact file to buy")

    def update(self, request, *args, **kwargs):
            file_obj = File.objects.get(pk = int(kwargs['pk']))
            cart_tuple = Cart.objects.get_or_create(user = request.user)
            cart_obj = cart_tuple[0]

            if request.data['buy_confirmation'] == 'buy':
                if not cart_obj.baught_files:
                    cart_obj.baught_files = []
                
                if file_obj.id not in cart_obj.baught_files:
                    cart_obj.baught_files.append(file_obj.id)
                    cart_obj.save()
                else:
                    return Response("You have already baught this file")

                return Response("You baught this file successfully")

            else:
                if file_obj.id not in cart_obj.baught_files:
                    return Response("You canceled buying this file")
                else:
                    return Response("You have already baught this file")

    def partial_update(self, request, *args, **kwargs):
        return None

    def destroy(self, request, *args, **kwargs):
        return Response("You do not have the permission to delete this file")

class ShowMyCartViewSet(ReadOnlyModelViewSet):
    ''' users can see their carts ''' 

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = Cart.objects.filter(user = self.request.user)
        return query

    serializer_class = ShowMyCartSerializer

class ShowSubscriptionViewSet(ModelViewSet):
    ''' users can see subscriptions and buy them ''' 

    permission_classes = [IsAuthenticated]

    queryset = Subscription.objects.all()

    serializers = {
        'list' : ShowSubscriptionSerializer,
        'retrieve' : ShowSubscriptionDetailSerializer,
        'create' : Go_To_Buy_Step,
        'update' : BuySubscription,
        'partial_update' : BuySubscription
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action)

    def check_subscription(self, cart_obj, sub_obj):
        utc=pytz.UTC

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
    
    def buy_subscription(self, cart_obj, sub_obj):
        cart_obj.baught_subscriptions.add(sub_obj)
        cart_obj.date_of_buying_subscription = datetime.now()
        cart_obj.save()

        return Response("You baught this file successfully")
    
    def create(self , request):
        return Response("Please select an exact subscription to buy")

    def update(self, request, *args, **kwargs):
            sub_obj = Subscription.objects.get(pk = int(kwargs['pk']))
            cart_tuple = Cart.objects.get_or_create(user = request.user)
            cart_obj = cart_tuple[0]

            if request.data['buy_confirmation'] == 'buy':
                try:
                    cart_obj.baught_subscriptions.get(id = sub_obj.id)
                except:
                    self.buy_subscription(cart_obj, sub_obj)
                else:
                    if self.check_subscription(cart_obj, sub_obj):
                        return Response("You have already baught this file")
                    else:
                        self.buy_subscription(cart_obj, sub_obj)

            else:
                try:
                    cart_obj.baught_subscriptions.get(id = sub_obj.id)
                except:
                    return Response("You canceled buying this file")
                else:
                    if self.check_subscription(cart_obj, sub_obj):
                        return Response("You have already baught this file")
                    else:
                        self.buy_subscription(cart_obj, sub_obj)

    def partial_update(self, request, *args, **kwargs):
        return None

    def destroy(self, request, *args, **kwargs):
        return Response("You do not have the permission to delete this subscription")

class ShowStoreViewSet(ReadOnlyModelViewSet):
    ''' users can see stores ''' 

    permission_classes = [IsAuthenticated]

    queryset = Store.objects.all()
    serializer_class = ShowStoreSerializer