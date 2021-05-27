from decimal import Decimal
from django.conf import settings


def bag_contents(request):

    '''
    Instead of returning a template, this function
    will return a dictionary called context. This is
    what's known as a context processor and its purpose
    is to make this dictionary available to all templates
    across the entire application, much like how you can use
    request.user in any template due to the presence of the
    built-in request context processor.

    To make this context processor available to the
    entire application we need to add it to the list of
    context processors in the templates variable in settings.py.

    This means that anytime we need to access the bag contents
    in any template across the entire site they'll be available to
    us without having to return them from a whole bunch of different
    views across different apps.
    '''

    bag_items = []
    total = 0   
    product_count = 0

    if total < settings.FREE_DELIVERY_THRESHOLD:
        # Decimal is preferrable over float when working with money as
        # it's more accurate
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE/100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total

    # Add variables to context to make them available across the site
    context = {
        'bag_items': bag_items,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
