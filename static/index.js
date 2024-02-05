console.log("Sanity check!");

const stripe = Stripe('pk_test_123');

initialize();

// Fetch Checkout Session and retrieve the client secret
async function initialize() {
  const response = await fetch("/create-checkout-session", {
    method: "POST",
  });

  const { clientSecret } = await response.json();

  const checkout = await stripe.initEmbeddedCheckout({
    clientSecret,
  });

  // Mount Checkout
  checkout.mount('#checkout');
}