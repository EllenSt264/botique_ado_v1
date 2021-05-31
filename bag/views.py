from django.shortcuts import render, redirect

# Create your views here.


def view_bag(request):
    """ A view that renders the bag content page """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to shopping bag """

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')

    # Get the bag variable if it exists in the session, or
    # create it as a new dictionary if it doesn't
    bag = request.session.get('bag', {})

    # Add item to bag or update quantity if it already exists
    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        bag[item_id] = quantity

    # Overwrite the variable in the session with the updated version
    request.session['bag'] = bag
    return redirect(redirect_url)
