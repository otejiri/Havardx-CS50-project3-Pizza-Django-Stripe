from django import template

register = template.Library()
# Create your views here.
@register.filter(name='stripeconversion')
def stripe_value(total_price):
    return str(int(round(total_price, 2) * 100))

@register.filter
def running_total(sales_list):
    return sum(d.amount for d in sales_list)