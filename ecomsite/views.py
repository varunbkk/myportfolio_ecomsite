from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime as dt
from .models import *
from .utils import cookieCart,cartData,guestOrder
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView,CreateView
from . import forms
from django.urls import reverse_lazy

def store(request):

	data = cartData(request)
	cartItems = data['cartItems']
	products = Product.objects.all()

	context = {'products':products,'cartItems':cartItems}
	return render(request, 'ecomsite/store.html', context)

def products(request):
	is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
	if is_ajax:
		if request.method == 'GET':
			sort_param = request.GET.get('sortid')
			if sort_param in ('name','price','id'):
				products = Product.objects.order_by(sort_param)
				data = products.values()

			return JsonResponse(list(data),safe=False)

def clearCart(request):
	# Receives the ajax call from the backend store.html script
	is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
	if is_ajax:
		if request.method == 'POST':
			data = json.load(request)
			action = data.get('action')

			customer = request.user.customer
			order = Order.objects.get(customer=customer,complete=False)
			orderItem = OrderItem.objects.filter(order=order)

		if action == 'clear':
			orderItem.delete()

		return JsonResponse(data,safe=False)

def cart(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'ecomsite/cart.html', context)

def checkout(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'ecomsite/checkout.html', context)

# When a logged in user clicks "add to cart", we want to send this data to a view to proccess this action.
# This is that view that is receiving the data from the frontend via the cart.js script
def updateItem(request):
    # Parsing the data received from cart.js
	data = json.loads(request.body)
    # We can access 'productId' and 'action' values as a Python dictionary
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
    # We used productId to query the product when the order is being created or updated
	product = Product.objects.get(id=productId)
    # We used get_or_create in order to work with the status False, which means the order is not completed
    # since it is an open cart
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # We used get_or_create because we want to have the ability to update the order item qty in the cart page
    # using the "add action -> (+) sign instead of creating a new one each time"
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

# View to process the order after the checkout form

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def processOrder(request):
	transaction_id = dt.datetime.now().timestamp()
	# Parses the data from the form on the frontend
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)

	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	email = data['form']['email']
	order.transaction_id = transaction_id
	# Checks if the order total is same as the cart Total
	if total == float(order.get_cart_total):
		order.complete = True
	order.customer = customer
	order.save()
	# This creates an instance of the ShippingAddress object
	# The information is retrieved from the shipping object that we sent from the frontend

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode']
		)
	return JsonResponse('Payment submitted..',safe=False)

class HowtoView(TemplateView):
	template_name = 'howto.html'
	# We need to show the cart total on each page - this is what the get function does
	def get(self,request):
		data = cartData(request)
		cartItems = data['cartItems']
		context = {'cartItems':cartItems}
		return render(request, 'ecomsite/getting_started.html', context)

# This function provides the logged-in user with a summary of their historical orders
@login_required
def order_list(request):
	# Same as above, We need to show the cart total on each page
	data = cartData(request)
	cartItems = data['cartItems']

	if request.user.is_authenticated:
		customer = request.user.customer
		# We filter out only completed orders
		orders = Order.objects.filter(customer=customer, complete=True)

	context = {'orders':orders,'cartItems':cartItems}
	return render(request, 'ecomsite/order_list.html', context)

# Sign up form for new users - using Django's UserCreationForm
class Signup(CreateView):
	form_class = forms.UserCreateform
	success_url = reverse_lazy('login')
	template_name = 'ecomsite/signup.html'

# Thank you page
def thank_you(request):
	data = cartData(request)
	cartItems = data['cartItems']
	context = {'cartItems':cartItems}
	return render(request,'ecomsite/thankyou.html',context)

# Product detail page
def product_detail(request,id):
	data = cartData(request)
	cartItems = data['cartItems']

	product = Product.objects.get(id=id)
	context = {'product':product,'cartItems':cartItems}
	return render(request,'ecomsite/product_detail.html',context)
