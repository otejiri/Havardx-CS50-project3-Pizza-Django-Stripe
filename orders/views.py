from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
from django.contrib import messages
from decimal import Decimal
from .models import ItemCost, Inventory, Order, Topping, ToppingCount, Completed_Order_Ids
import stripe
import datetime
from django.conf import settings
from django.core.paginator import Paginator

#stripe api
stripe.api_key = settings.STRIPE_SECRET_KEY # new


def index(request):
    #check if logged in
    if request.user.is_authenticated:
        request.session['username'] = request.user.username
        #check if loggedin and admin and go to orders
        if request.user.is_staff:
           return HttpResponseRedirect(reverse("orders"))
       #if not admin and logged in go to home
        else:
            return HttpResponseRedirect(reverse("pizza"))
   
    return render(request, 'home/index.html')

#stripe charge function
def charge(request):
    if request.method == 'POST':
        total_id=request.POST['ids']
        #listing id's of purchased items
        l = total_id.replace(']','').replace('[','')
        #converting the id's list to array to as to loop over them in receipt
        total_id_list = l.replace('"','').split(",")
        
        
        for each in total_id_list:
            ordered_item = Order.objects.get(pk=each)
            
            #check if any item in cart has already been paid for
            if ordered_item.status != 0:
                context = {
                "error_message": "Cart error, please try transaction again or contact support."
                }
                return render(request, 'user/charge_error.html', context)
        try:
            charge = stripe.Charge.create(
            amount=int(float(request.POST.get("amount", "")) * 100),
            currency='usd',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
            #storing stripe charge ID to use as transaction identifier
            create_id = Completed_Order_Ids.objects.create(order_id=charge.id)
            create_id.save()
            for i in total_id_list:
                b_item = Order.objects.get(pk=i)
                b_item.status = 1
                b_item.order_id = create_id
                b_item.save()
                
            purchased_item = Order.objects.all()
            #passing variables to receipt/success page
            context = {
                          "items": purchased_item,
                          "order_id": charge.id,
                          "date": datetime.date.today(),
                          "amount": request.POST.get("amount", ""),
                          "email": charge.billing_details.name,
                          } 
            #checking for errors in payment
        except stripe.error.CardError as e:
            
            
  # Since it's a decline, stripe.error.CardError will be caught
  
            context = {
                "error_message": e.error.message
            }
            return render(request, 'user/charge_error.html', context)
        except stripe.error.RateLimitError as e:
  # Too many requests made to the API too quickly
            context = {
                "error_message": "Oops our servers are facing unusual higher traffic, please try transaction again."
            }
            return render(request, 'user/charge_error.html', context)
        except stripe.error.InvalidRequestError as e:
  # Invalid parameters were supplied to Stripe's API
            context = {
                "error_message": "Invalid request, please try transaction again."
            }
            return render(request, 'user/charge_error.html', context)
        except stripe.error.AuthenticationError as e:
  # Authentication with Stripe's API failed
  # (maybe you changed API keys recently)
            context = {
                "error_message": "There is an error on our end, please try transaction again or contact support."
            }
            return render(request, 'user/charge_error.html', context)
        except stripe.error.APIConnectionError as e:
  # Network communication with Stripe failed
            context = {
                "error_message": "Network error, please try transaction again or contact support."
            }
            return render(request, 'user/charge_error.html', context)
        except stripe.error.StripeError as e:
  # Display a very generic error to the user, and maybe send
  # yourself an email
            context = {
                "error_message": "Transaction failed, please try transaction again or contact support."
            }
            return render(request, 'user/charge_error.html', context)
        except Exception as e:
  # Something else happened, completely unrelated to Stripe
            context = {
                "error_message": "Unknown error occurred, please try transaction again or contact support."
            }
            return render(request, 'user/charge_error.html', context)
    
        
        return render(request, 'user/payment_success.html', context)
    
@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='orders')          
def pizza(request):
    
    context = {
        "extra_allowed_count": 3
    }
    
    return render(request, "user/index.html", context)

#payment error page
def charge_error(request):
    
    
    return render(request, "user/charge_error.html")

@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='orders')    
def payment_success(request):
    
    return render(request, "user/payment_success.html")

@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='orders')    
def subs(request):
    
    context = {
        "extra_allowed_count": 5
    }
    
    return render(request, "user/subs.html", context)

@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='orders') 
def pasta(request):
    
    return render(request, "user/pasta.html")

def orders(request):
    current_user = request.user
    #pending orders status is stored in db as 1
    pending_orders = Order.objects.filter(status=1)
    
    pending_items_count = 0
        
    p_count = []
    #getting peding orders count to notify staff in the clock icon
    for each in pending_orders:
        p_count.append(each)
    
    pending_items_count = len(p_count)
    
    #filtering results of orders
    if request.GET.get('filter_status'):
        featured_filter = request.GET.get('filter_status')
        if not current_user.is_staff:
            orders_list = Order.objects.filter(status=featured_filter).order_by('-created_at')
        else:
            orders_list = Order.objects.filter(status=featured_filter)
    else:
        #if user is not staff latest order should come first
        if not current_user.is_staff:
            orders_list = Order.objects.all().exclude(status=0).order_by('-created_at')
        else:
            orders_list = Order.objects.exclude(status=0)
    
    
    orders = []
    customers = user = User.objects.all()
    for order in orders_list:
        if current_user.is_staff:
            orders = orders_list
        else:
            if order.user_id == current_user.id:
                orders.append(order)
        
    
    #paginator, 5 items per page
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    context = {
        "user_orders": orders,
        "customers": customers,
        "pending_items_count": pending_items_count
    }
    return render(request, "user/orders.html", context)

@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='orders') 
def salads(request):
    
    return render(request, "user/salads.html")

@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='orders') 
def dinner_platters(request):
    
    return render(request, "user/dinner_platters.html")

def admin_update_orders(request):
    # when staff update orders
    # pending = 0
    # completed = 1
    # refunded = 2
    set_status_value = request.POST["update"]
    item_id = request.POST["item_id"]
    item = Order.objects.get(pk=item_id)
    if set_status_value == 'pend':
        item.status = 1
    if set_status_value == 'confirm':
        item.status = 2
    if set_status_value == 'refund':
        item.status = 3
    item.save()
    return HttpResponseRedirect(reverse("orders"))

def delete_from_cart(request):
    item_id = request.POST["item_id"]
    
    user_order = Order.objects.get(pk=item_id)
    next = request.POST.get('next', '/')
    
    if user_order.status != 0:
        return HttpResponseRedirect(next)
    else:
        Order.objects.get(pk=item_id).delete()
        
        
        
    # after delete redirect to previous page
    return HttpResponseRedirect(next)

def register(request):
    if request.user.is_authenticated:
        request.session['username'] = request.user.username
        return HttpResponseRedirect(reverse("user"))
    else:
        return render(request, "home/register.html")


def login_user(request):
    username = request.POST["username"]
    password = request.POST["password"]
    
    if len(username) < 3:
        return render(request, "home/index.html", {"error": "Username must be greater than 3 char."})
    if len(password) < 3:
        return render(request, "home/index.html", {"error": "Password must be greater than 3 char."})
    
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        request.session['username'] = request.user.username
        if user.is_staff:
            return HttpResponseRedirect(reverse("orders"))
        else:
            return HttpResponseRedirect(reverse("pizza"))
            
    # A backend authenticated the credentials
    else:
        return render(request, "home/index.html", {"error": "Invalid login credentials."})
    # No backend authenticated the credentials

def logout_user(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(reverse("index"))

def add_to_cart(request):
    i = request.POST["item"]
    t = request.POST.getlist("toppings-selected")
    qty = request.POST["qty"]
    
    
    
    
    cart_item = ItemCost.objects.get(pk=i)
    item = cart_item.itemcost.get()
    price = cart_item.amount
    
    number_of_toppings = int(len(t))
    to_cart = Order.objects.create(qty=qty, status=0, amount=price, user_id=request.user.id)
    
    # check if item is customizable
    if item.customizable is True:
        for n in t:
            topping = Topping.objects.get(pk=n)
            to_cart.item_topping.add(topping)
        
        # loop over toppings
        for c in ToppingCount.objects.all():
            for p in c.inventory.all():
                if p.id == cart_item.id:
                    # check for amount of selected topping
                    if number_of_toppings == int(c.count):
                        # if subs then topping should add amount to price 
                        if str(item.item_type) == "subs":
                            price = price + c.amount
                        else:
                        # if not subs price should be topping price
                            
                            price = c.amount
    
    price = float(price) * int(qty)
        
    to_cart.item.add(cart_item)
    to_cart.amount = price
    
    
    to_cart.save()
    
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)
    

def create_user(request):

    username = request.POST["username"]
    password = request.POST["password"]
    first_name = request.POST["fname"]
    last_name = request.POST["lname"]
    email = request.POST["email"]

    if User.objects.filter(username=username).exists():
        return render(request, "home/register.html", {"error": "User with username already exists."})    
    if User.objects.filter(email=email).exists():
        return render(request, "home/register.html", {"error": "Email already exists."})
    if len(username) < 3:
        return render(request, "home/register.html", {"error": "Username must be greater than 3 char."})
    if len(password) < 3:
        return render(request, "home/register.html", {"error": "Password must be greater than 3 char."})
    if len(first_name) < 1:
        return render(request, "home/register.html", {"error": "First Name must be greater than 1 char."})
    if len(last_name) < 1:
        return render(request, "home/register.html", {"error": "Last Name must be greater than 1 char."})
    if len(email) < 3:
        return render(request, "home/register.html", {"error": "Email must be greater than 3 letters."})

    
    user = User.objects.create_user(username, email, password)
    user.last_name = last_name
    user.first_name = first_name
    
    user.save()
    
    return render(request, "home/index.html", {"success": "User registered succesfully, you can now login with your credentials"})  

