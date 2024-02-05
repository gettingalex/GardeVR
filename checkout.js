// This is your test publishable API key.
const stripe_keys = {
  "secret_key": process.env.STRIPE_SECRET_KEY,
  "publishable_key": process.env.STRIPE_PUBLISHABLE_KEY,
};
stripe.api_key = stripe_keys["secret_key"];

initialize();

// Create a Checkout Session as soon as the page loads
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