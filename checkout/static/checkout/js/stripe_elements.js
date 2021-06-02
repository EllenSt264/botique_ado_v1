/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// Slice off the first and last character as we don't want the quotation marks
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);

// Set up Stripe
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Stripe could potentially confirm the payment, but the user could close the
// page before the form in submitted, causing a payment in stripe but no
// order in the database. Or, if we were building a real store that 
// needed to complete post order operations like fulfillment 
// sending, internal email notifications etc, then none
// of that would be triggered because the user
// never fully completed their order.
// This could result in a customer being charged and never recieving 
// a confirmation email or even their order.
// To prevent this we're going to build some redunacy.


// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    // Before we call out Stripe, we want to disable both the
    // card element and submit button to prevent multiple submissions.
    // When the user submits the form, the card element is disabled
    // and the loading overlay is triggered.
    ev.preventDefault();
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    // The four variables below, capture the form data that we 
    // can't put in the payment intent. We then post it
    // to the cache_checkout_data view

    // Get boolean value of saved info box
    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // Object to pass this information to the new view and
    // pass the client secret for the payment intent
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    }

    var url = '/checkout/cache_checkout_data/';

    // Post data to the view

    // We use the done method to wait for a response that the payment intent
    // was updated before calling the confirmed payment method.
    $.post(url, postData).done(function() {
        // The view updates the payment intent and returns a 200 response, at which point we call
        // the confirmCardPayment method from stripe and if all is good, submit the form
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                // The trim method will remove any whitespace
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address: {
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            }
        }).then(function(result) {
            // If an error exists in the form
            if (result.error) {
                var errorDiv = document.getElementById('card-errors');
                var html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                // If there is an error we want to re-enable the card element, hide the overlay,
                // and submit button to allow the user to fix it.
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function() {
        // Reload the page to show the error from the view with django messages
        location.reload();
    })
});