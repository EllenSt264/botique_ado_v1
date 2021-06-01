from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem


"""
This is a special function that will handle signals on from
the post_save event. These parameters refer to:

* The sender of the signal (sent), which here is OrderLineItem

* The actual instance of the model that sent it (instance)

* A boolean sent by django referring to whether this is a new instance
or one being updated (created)

* And any keyword arguments (**kwags)

"""


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwags):
    """ Update order total on lineitem update/create """

    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwags):
    """ Update order total on lineitem delete """

    instance.order.update_total()
