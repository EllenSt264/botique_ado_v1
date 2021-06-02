  /*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// Slice off the first and last character as we don't want the quotation marks
var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
var client_secret = $('#id_client_secret').text().slice(1, -1);

var style = {
  base: {
    color: "#000",
    fontFamily: 'Arial, sans-serif',
    fontSmoothing: "antialiased",
    fontSize: "16px",
    "::placeholder": {
      color: "#aab7c4"
    }
  },
  invalid: {
    fontFamily: 'Arial, sans-serif',
    color: "#dc3545",
    iconColor: "#dc3545"
  }
};

// Set up Stripe
var stripe = Stripe(stripe_public_key);
var element = stripe.elements();
var card = element.create('card', {style: style});
card.mount('#card-element');



card.mount('#card-element');