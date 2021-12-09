from django.urls import path
from . import views

urlpatterns = [
    path('',views.store,name='store'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('update_item/',views.updateItem,name='update_item'),
    path('process_order/',views.processOrder,name='process_order'),
    path('getting_started/',views.HowtoView.as_view(),name='howto'),
    path('myorders/',views.order_list,name='list'),
    path('signup/',views.Signup.as_view(),name='signup'),
    path('thankyou/',views.thank_you,name='thank_you'),
    path('products/<int:id>/',views.product_detail,name='detail'),
    path('products/',views.products,name='products'),
    path('clear_cart/',views.clearCart,name='clearCart')
]
