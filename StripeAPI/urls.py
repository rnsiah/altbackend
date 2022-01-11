from django.urls import path
from . import views

app_name= 'StripeAPI'


urlpatterns = [
    path('stripe-checkout/', views.stripe_checkout.as_view(), name='stripe-checkout'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session, name ='create-checkout-session'),
    path('cancelled/', views.CancelledView.as_view(), name='cancelled'),
    path('success', views.SuccessView.as_view(), name='success'),
    path('webhook/', views.stripe_webhook),
]