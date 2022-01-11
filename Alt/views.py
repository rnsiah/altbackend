from django.shortcuts import render,get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Shirt, Atrocity, NonProfit, Order, OrderItem, CheckoutAddress
from django.contrib import messages
from api.models import User, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm



def home(request):
  return render (request, 'landing.html')






class UserDetailView(DetailView):
  model = UserProfile
  
   

  def get_object(self, queryset=None):
    
    return self.model.objects.filter(slug='slug')
    
  def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['shirt_list'] = Shirt.objects.all()
        context['atrocity_list']= Atrocity.objects.all()
        context['nonProfit_list'] = NonProfit.objects.all()
        context['slug'] = 'slug'

        return context



def dontation_page(request, slug):
  user = get_object_or_404(UserProfile, slug =slug)
  return render (request, 'user.html', {'user':user})


class ShirtList(ListView):
  model = Shirt
  template_name = 'allshirts_list.html'


  


def view_shirt(request, slug):
    shirt = get_object_or_404(Shirt, slug=slug)
    return render(request, 'shirt.html',{'shirt':shirt} )


@login_required
def add_to_cart(request, slug) :
  shirt = get_object_or_404(Shirt, slug = slug )
  order_item, created = OrderItem.objects.get_or_create(
    shirt=shirt,
    user = request.User,
    ordered = False
    )
  order_qs = Order.objects.filter(user=request.User, ordered= False)

  if order_qs.exists():
    order = order_qs[0]
        
    if order.items.filter(item__pk = shirt.pk).exists():
      order_item.quantity += 1
      order_item.save()
      messages.info(request, "Added quantity Item")
      return redirect("Alt:shirts", slug = slug)
    else:
      order.items.add(order_item)
      messages.info(request, "Item added to your cart")
      return redirect("Alt:shirts", slug = slug)
  else:
    ordered_date = timezone.now()
    order = Order.objects.create(user=request.User, ordered_date = ordered_date)
    order.items.add(order_item)
    messages.info(request, "Item added to your cart")
    return redirect("Alt:shirts", slug = slug)

@login_required
def remove_from_cart(request, slug):
    shirt = get_object_or_404(Shirt, slug=slug )
    order_qs = Order.objects.filter(
        user=request.User, 
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(shirt__slug=shirt.slug).exists():
            order_item = OrderItem.objects.filter(
                shirt=shirt,
                user=request.User,
                ordered=False
            )[0]
            order_item.delete()
            messages.info(request, "Item \""+order_item.ordered_shirt.name+"\" remove from your cart")
            return redirect("Alt:shirts", slug = slug)
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("Alt:shirts", slug=slug)
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("Alt:shirts", slug = slug)

class NonProfitList(ListView):
  model = NonProfit
  template_name = 'nonprofit_list.html'


def view_nonProfit(request, slug):
  nonprofit = get_object_or_404(NonProfit, slug=slug)
  return render(request,'nonprofit.html', {'nonprofit':nonprofit} )


class OrderSummaryView(LoginRequiredMixin, View):
  def get(self, *args, **kwargs):

    try:
      order = Order.objects.get(user=self.request.User, ordered =False)
      context={
        'object':order
      }
      return render(self.request, 'order_summary.html', context)
    except ObjectDoesNotExist:
      messages.error(self.request, 'You do not have an order')
      return redirect ('/')


@login_required
def reduce_quantity_from_cart(request, slug):
  shirt = get_object_or_404(Shirt, slug=slug)
  order_qs = Order.objects.filter(
    user = request.User, 
    ordered = False
  )
  if order_qs.exists():
    order = order_qs[0]
    if order.shirts.filter(shirt__slug=shirt.slug).exists():
      ordered_shirt = OrderItem.objects.filter(
        ordered_shirt = shirt,
        user = request.User,
        ordered = False
      )[0]
      if ordered_shirt.qauntity > 1:
        ordered_shirt.quantity -=1
        ordered_shirt.save
      else:
        ordered_shirt.delete()
      messages.info(request, 'Item quantity has been updated')
      return redirect('Alt:order-summary')
    else:
      messages.info(request, 'This item is not in your cart')
      return redirect("Alt:order-summary")
  else:
    messages.info(request, "You have not started an order")
    return redirect("Allt:order-summary")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        
        try:
            order = Order.objects.get(user=self.request.User, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                checkout_address = CheckoutAddress(
                    user= self.request.User,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                checkout_address.save()
                order.checkout_address = checkout_address
                order.save()
                return redirect('Alt:checkout')
            messages.warning(self.request, "Failed Chekout")
            return redirect('Alt:checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("Alt:order-summary")

  