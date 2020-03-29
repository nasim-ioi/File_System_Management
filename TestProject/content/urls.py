from django.urls import path, include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .views import (FileUploadViewSet, ProductViewSet, SubscriptionViewSet, 
                   ShowProductViewSet, ShowFileViewSet, ShowMyCartViewSet,
                   ShowSubscriptionViewSet, ShowStoreViewSet)


router = DefaultRouter()
router.register('upload_file', FileUploadViewSet, basename='upload_file')
router.register('add_product', ProductViewSet, basename='add_product')
router.register('add_subscription', SubscriptionViewSet, basename='subscription')
router.register('show_products', ShowProductViewSet, basename='show_product')
router.register('show_files', ShowFileViewSet, basename='show_file')
router.register('show_my_cart', ShowMyCartViewSet, basename='cart')
router.register('show_subscription', ShowSubscriptionViewSet, basename='show_subscription')
router.register('show_store', ShowStoreViewSet, basename='show_store')

urlpatterns = [
   path('', include(router.urls)),
]