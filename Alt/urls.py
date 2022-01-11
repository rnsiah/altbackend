from django.urls import path
from .views import home, ShirtList, view_shirt, NonProfitList, view_nonProfit, add_to_cart, remove_from_cart, OrderSummaryView, reduce_quantity_from_cart,CheckoutView, UserDetailView, dontation_page

app_name= 'Alt'

urlpatterns = [
    path('', home, name='landing'),
    path('allshirts', ShirtList.as_view(), name = 'allshirts_list'),

    path('true/<slug>',  dontation_page, name= 'user'),
    path('shirt/<slug>/', view_shirt, name = 'shirt' ),
    path('all_nonprofits', NonProfitList.as_view(), name='nonprofit_list'),
    path('nonprofit/<slug>', view_nonProfit, name='nonprofit' ),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/',remove_from_cart, name='remove-from-cart' ),
    path('order-summary', OrderSummaryView.as_view(), name ='order_summary'),
    path('reduce-quantity-from-cart/<slug>/', reduce_quantity_from_cart, name='reduce-quantity-from-cart'),
    path('chekout', CheckoutView.as_view(), name='checkout'),
    

    
    
   
]



