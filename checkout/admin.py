from django.contrib import admin
from .models import Order, OrderLineItem

# Register your models here.


# The inline admin class will inherit from admin.TabularInline. 
# This inline item is going to allow us to add and edit line
# items in the admin right from inside the order model. So
# when we look at an order, we'll see a list of editable
# editable line items on the same page rather than
# having to go to the order line item interface.

class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    # These will be calculated by our model methods,
    # so we don't want the ability to edit them
    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'original_bag',
                       'stripe_pid')

    # This will allow us to specifty the order of the fields
    # in the admin interface which would otherwise be
    # adjusted by django due to the use of
    # some read-only fields.
    fields = ('order_number', 'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total', 'original_bag',
              'stripe_pid')

    # This will restrict the columns that show up in the order
    # list to only a few key items.
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost', 'grand_total')

    # Order by date in reverse chronological order,
    # puttin the most recent orders at the top.
    ordering = ('-date',)


# Don't need to register the OrderLineItem model as it's
# accessible via the inline on the order model.
admin.site.register(Order, OrderAdmin)
