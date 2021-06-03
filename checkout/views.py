from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe
import json


# Before we call the card payment in the stripe javascript file,
# we'll make a post request to this view and give it the
# client secret from the payment intent.
@require_POST
def cache_checkout_data(request):
    """ Add saved info to payment intent in metadata key """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Create order in database for the checkout page is submitted
    if request.method == "POST":
        bag = request.session.get('bag', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # Create an instance of the form using form_data
        order_form = OrderForm(form_data)

        # If the form is valid we can save the order
        if order_form.is_valid():
            # Prevent multiple saves by using commit=False
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            # Iterate through the bag items to create each line item
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    # If the value of product is an integer than we know that
                    # the product does not have sizes so the quantity
                    # will just be the item_data
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        # If the item has sizes, iterate through each size and
                        # create a line item accordingly
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please contact us for assistance!"
                    ))
                    order.delete()
                    return redirect(reverse('view_bag'))

            # Attach whether or not the user wanted to save their profile 
            # information to the session and then redirect them to a
            # new page called checkout success
            request.session['save_info'] = 'save_info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    # Handle the get requests
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        # Store the bag_content in a new variable so not to overwrite the original
        current_bag = bag_contents(request)
        total = current_bag['grand_total']

        # Stripe requires the amount to charge as an integer, so we'll
        # multiply the total by 100 and round to zero decimal places
        stripe_total = round(total * 100)

        # Set secret key on stripe
        stripe.api_key = stripe_secret_key

        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        order_form = OrderForm()

    # Alert message for if public key is missing
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)



def checkout_success(request, order_number):
    """ Handle successful checkouts """

    # Check whether the user want to save their profile
    # information by getting that from the session
    # just like we get the shopping bag
    save_info = request.session.get('save_info')

    # Use order number to get the order from the previous
    # view which we will send back to the template,
    # and attach a success message letting the
    # user know what their order number is
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order Successfully processed! \
        Your order number is {order_number}. A confirmation \
            email will be sent to {order.email}.')

    # Delete shopping bag from the session
    if 'bag' in request.session:
        del request.session['bag']
    
    # Set the template and the context
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
