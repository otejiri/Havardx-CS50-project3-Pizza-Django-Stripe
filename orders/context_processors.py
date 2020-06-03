from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from .models import ItemCost, Inventory, Order, Topping, ToppingCount
from decimal import Decimal
from django.conf import settings # new

def data(request):
    if not request.user.is_authenticated:
        return {
            "": ""
        }
    else:
        def get_context_data(self, **kwargs): # new
            key = super().get_context_data(**kwargs)
        
        orders = Order.objects.filter(user_id=request.user.id)
        
        total = Decimal(0)
        cart_item_count = 0
        
        total_id = []
        for order in orders:
           if order.status == 0:
               total_id.append(order.id)
               cart_item_count = len(total_id)
               total += Decimal(order.amount)
               
        
                
            
            
        return {
            "inventory": Inventory.objects.all(),
            "itemcost": ItemCost.objects.all(),
            "orders": orders,
            "total": total,
            "key": settings.STRIPE_PUBLISHABLE_KEY,
            "total_id": total_id,
            "cart_item_count": cart_item_count
        }
        return render(request, "user/index.html")