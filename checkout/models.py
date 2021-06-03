# UUID will generate the order number

import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings

from products.models import Product


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')

    # The function is prepended with an underscore by convention
    # to indicate it is a private method.
    def _generate_order_number(self):
        """ Generate a random, unique order number using UUID  """

        # generate a random string of 32 characters
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """ Update grand total each time a line item is added """

        # This works by using the sum function across all the line-item
        # total fields for all line items in this order. The default
        # behaviour is to add a new field to the query set called
        # lineitem_total_sum, which we can get and then set
        # the order total to that.

        # The 'or 0' will prevent an error if we manually delete all the
        # line items from an order by making sure that this sets the
        # order total to zero instead of none.
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0

        # With the order total calculated we can calculate the delivery cost
        # using the free delivery threshold and standard delivery
        # percentage from our settings file.
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0

        # Add order total and delivery total together to calculate grand total
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """ Override original save method to set order number """

        # If the order we're saving doesn't have an order number,
        # then call the generate order number function and
        # execute the original save method.
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


"""
    When a user checks out, we'll first use the information they put
    into the payment form to create an order instance, then we'll
    iterate through the items in the shopping bag, creating
    an order line item for each one, attaching it to the
    order and updating the delivery cost, order total,
    and grand total along the way.
"""


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=2, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    # Set the line-item total field by overriding its save method
    def save(self, *args, **kwargs):
        """ Override original save method to set order number """

        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'
