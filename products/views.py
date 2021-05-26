from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category

# Create your views here.


def all_products(request):
    """ A view to display all products, including sorting and searching queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        # First we check if 'sort' is in request.get
        if 'sort' in request.GET:
            # Set 'sort' equal to sort and sortkey
            # We copy the sort parameter into a new variable called 
            # sortkey in order to preserve the original field we want to sort on that name
            sortkey = request.GET['sort']
            sort = sortkey

            # In order to allow case-insensitive sorting on a name field, we need
            # to first annotate all products with a new field.
            # Annotation allows us to add temporary field on a model, so in this
            # case, we want to check whether sortkey is equal to name.
            if sortkey == 'name':
                # Rename sortkey to 'lower_name' in the event that the user is sorting by name
                # lower_name is the actual field we're going to sort on within the sortkey variable
                sortkey = 'lower_name'
                # Annotate the current list of products with a new field
                products = products.annotate(lower_name=Lower('name'))

            if sortkey == 'category':
                sortkey = 'category__name'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                # Check if the direction is descending in order to decided whether to reverse the order
                if direction == 'desc':
                    sortkey = f'-{sortkey}'

            # Use the order_by method to sort the products
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    # return the sorting methodology to the template
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)