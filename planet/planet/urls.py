from django.urls import path
from orders.views import ordersPage, newOrder, orderItems, addOrder, confirmPayment, summary

urlpatterns = [
    path('', ordersPage, name="orders-page"),
    path('new-order', newOrder, name="new-order"),
    path('items', orderItems, name="items"),
    path('add-order', addOrder, name="add-order"),
    path('confirm-payment', confirmPayment, name="confirm-payment"),
    path('summary', summary, name="summary")
]
