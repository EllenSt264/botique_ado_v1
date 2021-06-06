from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    # Specify that the product id should be an integer to prevent django
    # from interpreting the string as the id, which would throw an error
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>', views.delete_product, name='delete_product'),
]
