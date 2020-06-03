from django.urls import path
from django.contrib.auth.decorators import user_passes_test


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("auth", views.create_user, name="create_user"),
    path("login", views.login_user, name="login_user"),
    path("logout", views.logout_user, name="logout_user"),
    path("add_to_cart", views.add_to_cart, name="add_to_cart"),
    path("pizza", views.pizza, name="pizza"),
    path("subs", views.subs, name="subs"),
    path("pasta", views.pasta, name="pasta"),
    path("salads", views.salads, name="salads"),
    path("dinner_platters", views.dinner_platters, name="dinner_platters"),
    path("charge", views.charge, name='charge'),
    path("orders", views.orders, name='orders'),
    path("charge_error", views.charge_error, name='charge_error'),
    path("delete_from_cart", views.delete_from_cart, name="delete_from_cart"),
    path("payment_success", views.payment_success, name="payment_success"),
    path("admin_update_orders", views.admin_update_orders, name="admin_update_orders")
    
    
    
]
