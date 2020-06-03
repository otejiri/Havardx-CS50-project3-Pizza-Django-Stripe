from django.contrib import admin

from .models import Inventory, Topping, ItemCost, ToppingCount, Order, ItemType, ItemSize, Completed_Order_Ids

# Register your models here.
admin.site.register(Inventory)
admin.site.register(Topping)
admin.site.register(ItemCost)
admin.site.register(ToppingCount)
admin.site.register(Order)
admin.site.register(ItemType)
admin.site.register(ItemSize)
admin.site.register(Completed_Order_Ids)





