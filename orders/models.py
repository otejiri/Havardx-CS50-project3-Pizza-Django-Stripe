from django.db import models

# Create your models here.

# sizes of items (small, large etc)
class ItemSize(models.Model):
    name = models.CharField(max_length=64, blank=True)
    
    def __str__(self):
        return f"{self.name}"
    
# type of items (pizza, subs, salads etc)
class ItemType(models.Model):
    item = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.item}"

# list of toppings  
class Topping(models.Model):
    item = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.item}"
    
# all items for sale 
class Inventory(models.Model):
    name = models.CharField(max_length=64)
    toppings = models.ManyToManyField(Topping, blank=True, related_name="toppings")
    special = models.BooleanField(default=False)
    customizable = models.BooleanField(default=True)
    item_type = models.ForeignKey(ItemType, on_delete=models.PROTECT, null=True)
    comments = models.CharField(max_length=500, blank=True)
    
    
    
    def __str__(self):
        return f"{self.name}"
    

# price function
class ItemCost(models.Model):
    name = models.ForeignKey(ItemSize, on_delete=models.PROTECT, blank=True, null=True)
    itemcost = models.ManyToManyField(Inventory, blank=True, related_name="cost")
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    
    
    def __str__(self):
        for each in self.itemcost.all():
            return f"{self.name} {each}"
        

    
    
class ToppingCount(models.Model):
    count = models.CharField(max_length=64)
    inventory = models.ManyToManyField(ItemCost, blank=True, related_name="toppingcount")
    amount = models.DecimalField(max_digits=6, null=True, decimal_places=2)
    
    def __str__(self):
        for each in self.inventory.all():
            return f"{self.count} toppings for {each} {self.amount}"

class Completed_Order_Ids(models.Model):
    order_id = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.order_id}"

# models for orders          
class Order(models.Model):
    qty = models.IntegerField()
    item = models.ManyToManyField(ItemCost, blank=True, related_name="item")
    item_topping = models.ManyToManyField(Topping, blank=True, related_name="item_topping")
    order_id = models.ForeignKey(Completed_Order_Ids, on_delete=models.PROTECT, null=True)
    status = models.IntegerField()
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    user_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        get_latest_by = ['item']
        
    def __str__(self):
        for each in self.item.all():
            return f"{each} {self.amount} {self.item_topping.all()}"


    
    

    

    

    

    
    