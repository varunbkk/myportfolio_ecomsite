import json
from .models import *

# We use the cookieCart function to build the order for a guest user, based on cookie data
def cookieCart(request):
    # We want to get the cart content from the cookies in the browser
    # json.loads() converts the string, back into a Python dictionary
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart:',cart)
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
    cartItems = order['get_cart_items']
    # We need to loop through the cart object to calculate the total items that
    # the guest user has in their cart
    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            # Gets the id of the product based off the i which is iterating through our cart object
            product = Product.objects.get(id=i)
            # Gets the product total based on the product price and item quantiy
            total = (product.price * cart[i]['quantity'])
            # Gets the cart total based off the sum total of the product total
            order['get_cart_total'] += total
            # Gets the total qty of items in the cart
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'id':product.id,
                'product':{
                'id':product.id,
                'name':product.name,
                'price':product.price,
                'digital':product.digital,
                'imageURL':product.imageURL
                },
                'quantity':cart[i]['quantity'],
                'get_total':total
            }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True

        except:
            pass

    return {'cartItems':cartItems,'order':order,'items':items}

# cartData function helps to process the order, based on whether the user is registered or a guest
def cartData(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		cookieData = cookieCart(request)
		cartItems = cookieData['cartItems']
		order = cookieData['order']
		items = cookieData['items']

	return {'cartItems':cartItems ,'order':order, 'items':items}

# This function helps to process an order for a guest user
def guestOrder(request, data):
    print('User is not logged in..')
    # We're building our cart data using the cookie cart function
    print('COOKIES:',request.COOKIES)
    # We need to query our items and build the order from the cookie data
    first_name = data['form']['first_name']
    last_name = data['form']['last_name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']
    # Now we need to create the customer
    # This statement is especially useful because it helps to capture the customers email
    # based on his previous shoppign history, even if they were not a registered user
    # If the user registers with this email that was previously provided
    # All the order history associated with the email will be visible, once the user finally registers
    customer, created = Customer.objects.get_or_create(email=email)
    customer.first_name = first_name
    customer.last_name = last_name
    customer.save()

    #Create the order and assign it to the customer we just set above
    # Complete is false since the order is not completed
    order = Order.objects.create(customer=customer,complete=False)
    # We loop through our cart item list and create real OrderItem items by querying the product
    for item in items:
        product = Product.objects.get(id=item['id'])
        # Creating the order item here
        orderItem = OrderItem.objects.create(product=product,order=order,quantity=item['quantity'])

    return customer, order
