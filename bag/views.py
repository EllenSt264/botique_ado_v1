from django.shortcuts import render, redirect

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
