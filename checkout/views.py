from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

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
        message.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)
