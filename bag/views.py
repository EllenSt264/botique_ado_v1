from django.shortcuts import render, redirect, reverse, HttpResponse

# Create your views here.


def view_bag(request):
    """ A view that renders the bag content page """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to shopping bag """

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')

    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']

    # Get the bag variable if it exists in the session, or
    # create it as a new dictionary if it doesn't
    bag = request.session.get('bag', {})

    # Check if a product with sizes is being added
    if size:

        # If the item is already in the bag
        if item_id in list(bag.keys()):
            # Check if another item of the same id and size exists,
            # and if so, increment the quantity for that size.
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['item_by_size'][size] += quantity
            # Otherwise set it equal to the quantity since the item
            # already exists in the bag, but this is a new size
            # for that item.
            else:
                bag[item_id]['items_by_size'][size] = quantity

        # If the items are not already in the bag then add it, but we're
        # going to do it as a dictionary with a key of 'items_by_size'
        # since we may have multiple items with this item id,
        # but with different sizes.
        # This allows us to have a single item id for each item,
        # but still track multiple sizes.
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}

    # If there's no size
    else:
        # Add item to bag or update quantity if it already exists
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

    # Overwrite the variable in the session with the updated version
    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """ Adjust the quantity of the specified product to the specified amount """

    quantity = int(request.POST.get('quantity'))

    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']

    bag = request.session.get('bag', {})

    # If there's a size, we need to drill into the items by size dictionary
    # find that specific size and either set its quantity to the updated one or
    # remove it if the quantity submitted is zero
    if size:
        # If quantity is greater than zero we set items quantity accordingly
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
        # Otherwise we want to remove the item
        else:
            del bag[item_id]['items_by_size'][size]
            # If there's only one size in the bag then the items_by_size
            # dictionary will be empty and evalute to false, so we
            # want to remove the entire item id so we don't end
            # up with an empty items_by_size dictionary.
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
    else:
        if quantity > 0:
            bag[item_id] = quantity
        else:
            bag.pop(item_id)

    request.session['bag'] = bag
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """ Remove item from shopping bag """

    # Wrap this entire block of code in a try block,
    # and catch any exceptions that happen in
    # order to return a 500 server error.
    try:
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']

        bag = request.session.get('bag', {})

        # If there's a size, we only want to remove the specific size
        # that the user requested, so we want to delete that size
        # key in the items_by_size dictionary.
        if size:
            del bag[item_id]['items_by_size'][size]
            # If there's only one size in the bag then the items_by_size
            # dictionary will be empty and evalute to false, so we
            # want to remove the entire item id so we don't end
            # up with an empty items_by_size dictionary.
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
        else:
            bag.pop(item_id)

        request.session['bag'] = bag

        # Instead of returning redirect, because this is a JavaScript
        # function, we want to return an actual 200 HTTP response,
        # implying that the item was successfully removed.
        return HttpResponse(status=200)

    # Use variable e, to return an actual
    # error in case anything goes wrong
    except Exception as e:
        return HttpResponse(status=500)
