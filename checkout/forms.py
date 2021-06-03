from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county')

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """

        # We call the default init method to set the form up
        # as it would be by default.
        super().__init__(*args, **kwargs)

        # Create dictionary of placeholders that will show up
        # in the form fields.
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

        # Set the autofocus attribute on the full name field to true
        # so the cursor will start in the full name field when
        # the user loads the page.
        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            # To prevent an error due to country not having a placeholder
            if field != 'country':
                # Iterate through the form's fields, adding a star if it's
                # a required field on the model
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]

                # Set all the placeholder attributes to their values in the
                # dictionary defined above
                self.fields[field].widget.attrs['placeholder'] = placeholder

            # Add a CSS class that we'll use later
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'

            # Remove the form field labels as we no longer need them
            self.fields[field].label = False
