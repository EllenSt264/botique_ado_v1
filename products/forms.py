from django import forms
from .models import Category, Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Display categories with their friendly name
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        # Set classes on fields so they match the site's theme
        self.fields['category'].choices = friendly_names
        for friendly_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
